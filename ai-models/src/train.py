"""
train.py — Huấn luyện & tinh chỉnh tham số cho bài toán Phân loại nấm ăn được/độc.

Thiết kế quan trọng: mỗi model được bọc trong 1 sklearn Pipeline gồm
  bước 'prep' (ColumnTransformer One-Hot, xem preprocess.py) + bước 'clf' (model).
GridSearchCV chạy trên toàn bộ Pipeline này với cross-validation trên TẬP TRAIN
=> ColumnTransformer được fit lại đúng cách trên từng fold, không rò rỉ dữ liệu
   giữa các fold và tuyệt đối không đụng vào tập test.
"""
import time
import json
from pathlib import Path

import joblib
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from preprocess import build_preprocessor

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
SCORING = "f1"  # ưu tiên cân bằng Precision/Recall vì 2 loại sai lầm đều quan trọng


def _pipeline(feature_cols, estimator):
    return Pipeline([
        ("prep", build_preprocessor(feature_cols)),
        ("clf", estimator),
    ])


def get_model_specs(feature_cols):
    """Trả về dict: tên model -> (pipeline chưa fit, param_grid để GridSearchCV)."""
    specs = {}

    specs["Baseline (Dummy)"] = (
        _pipeline(feature_cols, DummyClassifier(strategy="most_frequent", random_state=42)),
        {},  # không có tham số để tinh chỉnh
    )

    specs["Logistic Regression"] = (
        _pipeline(feature_cols, LogisticRegression(max_iter=2000, random_state=42)),
        {"clf__C": [0.01, 0.1, 1, 10, 100]},
    )

    specs["KNN"] = (
        _pipeline(feature_cols, KNeighborsClassifier()),
        {"clf__n_neighbors": [3, 5, 7, 9, 11, 15], "clf__weights": ["uniform", "distance"]},
    )

    specs["Random Forest"] = (
        _pipeline(feature_cols, RandomForestClassifier(random_state=42)),
        {"clf__n_estimators": [100, 200], "clf__max_depth": [None, 10, 20]},
    )

    specs["SVM (RBF)"] = (
        _pipeline(feature_cols, SVC(probability=True, random_state=42)),
        {"clf__C": [0.1, 1, 10], "clf__kernel": ["rbf", "linear"]},
    )

    return specs


def train_all(X_train, y_train, feature_cols, out_dir="../models/candidates"):
    """Chạy GridSearchCV cho từng model, đo thời gian train/predict, lưu từng pipeline tốt nhất.
    Trả về dict kết quả để dùng ở notebook 04_evaluate."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    specs = get_model_specs(feature_cols)
    results = {}

    for name, (pipe, grid) in specs.items():
        print(f"\n=== Huấn luyện: {name} ===")
        t0 = time.time()
        if grid:
            search = GridSearchCV(pipe, grid, cv=CV, scoring=SCORING, n_jobs=-1)
            search.fit(X_train, y_train)
            best_estimator = search.best_estimator_
            best_params = search.best_params_
            cv_best_score = search.best_score_
        else:
            pipe.fit(X_train, y_train)
            best_estimator = pipe
            best_params = {}
            cv_best_score = None
        train_time = time.time() - t0

        # Đo thời gian dự đoán trên 1 mẫu (mô phỏng 1 lần gọi API thực tế)
        t1 = time.time()
        _ = best_estimator.predict(X_train.iloc[:1])
        predict_time_ms = (time.time() - t1) * 1000

        safe_name = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        model_path = f"{out_dir}/{safe_name}.joblib"
        joblib.dump(best_estimator, model_path)
        file_size_kb = Path(model_path).stat().st_size / 1024

        print(f"  train_time={train_time:.2f}s | predict_time={predict_time_ms:.2f}ms | "
              f"file_size={file_size_kb:.1f}KB | best_params={best_params} | cv_{SCORING}={cv_best_score}")

        results[name] = {
            "model_path": model_path,
            "best_params": best_params,
            "cv_score": cv_best_score,
            "train_time_sec": round(train_time, 3),
            "predict_time_ms": round(predict_time_ms, 3),
            "file_size_kb": round(file_size_kb, 1),
        }

    with open(f"{out_dir}/train_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results


if __name__ == "__main__":
    from pathlib import Path as _Path
    from preprocess import load_raw_data, clean_data, get_feature_columns, encode_target, split

    ROOT = _Path(__file__).resolve().parents[1]  # ai-models/
    df_raw = load_raw_data(str(ROOT / "data" / "dataset.zip"))
    df_clean = clean_data(df_raw)
    feature_cols = get_feature_columns(df_clean)
    y, mapping = encode_target(df_clean)
    X_train, X_test, y_train, y_test = split(df_clean, feature_cols, y)

    results = train_all(X_train, y_train, feature_cols, out_dir=str(ROOT / "models" / "candidates"))
    print("\n--- Tóm tắt ---")
    for name, r in results.items():
        print(name, "->", r)
