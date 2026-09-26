"""
evaluate.py — Đánh giá các model ứng viên (Bước 3) trên TẬP TEST (chưa từng thấy),
chọn ra model cuối cùng để đóng gói ở Bước 5.1.

QUAN TRỌNG: đây là lần DUY NHẤT tập test được dùng. Không được quay lại chỉnh
tham số dựa trên kết quả test (nếu làm vậy, test set sẽ mất ý nghĩa "chưa từng thấy").
"""
import json
from pathlib import Path

import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)


def evaluate_all(candidates_dir: str, X_test, y_test) -> dict:
    """Load từng model .joblib trong candidates_dir, đánh giá trên X_test/y_test.
    Trả về dict: tên model -> các chỉ số."""
    candidates_dir = Path(candidates_dir)
    train_results = json.load(open(candidates_dir / "train_results.json", encoding="utf-8"))

    name_map = {
        "baseline_dummy": "Baseline (Dummy)",
        "logistic_regression": "Logistic Regression",
        "knn": "KNN",
        "random_forest": "Random Forest",
        "svm_rbf": "SVM",
    }

    results = {}
    for file_stub, display_name in name_map.items():
        model_path = candidates_dir / f"{file_stub}.joblib"
        pipe = joblib.load(model_path)

        y_pred = pipe.predict(X_test)
        try:
            y_proba = pipe.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, y_proba)
        except Exception:
            auc = None

        cm = confusion_matrix(y_test, y_pred).tolist()  # [[TN,FP],[FN,TP]]

        train_info = next((v for k, v in train_results.items() if v["model_path"].endswith(f"{file_stub}.joblib")), {})

        results[display_name] = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y_test, y_pred, zero_division=0), 4),
            "roc_auc": round(auc, 4) if auc is not None else None,
            "confusion_matrix": cm,  # [[TN, FP], [FN, TP]]
            "train_time_sec": train_info.get("train_time_sec"),
            "predict_time_ms": train_info.get("predict_time_ms"),
            "file_size_kb": train_info.get("file_size_kb"),
            "best_params": train_info.get("best_params"),
            "model_path": str(model_path),
        }
    return results


def pick_best(results: dict, exclude=("Baseline (Dummy)",)) -> str:
    """Chọn model tốt nhất: ưu tiên F1 cao nhất trên test; nếu bằng nhau (làm tròn 4 chữ số),
    ưu tiên thời gian dự đoán thấp hơn, rồi đến kích thước file nhỏ hơn."""
    candidates = {k: v for k, v in results.items() if k not in exclude}
    best_name = min(
        candidates,
        key=lambda k: (-candidates[k]["f1"], candidates[k]["predict_time_ms"], candidates[k]["file_size_kb"])
    )
    return best_name


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from preprocess import load_raw_data, clean_data, get_feature_columns, encode_target, split

    ROOT = Path(__file__).resolve().parents[1]
    df_raw = load_raw_data(str(ROOT / "data" / "dataset.zip"))
    df_clean = clean_data(df_raw)
    feature_cols = get_feature_columns(df_clean)
    y, mapping = encode_target(df_clean)
    X_train, X_test, y_train, y_test = split(df_clean, feature_cols, y)

    results = evaluate_all(str(ROOT / "models" / "candidates"), X_test, y_test)

    print(f"{'Model':<22}{'Acc':>8}{'Prec':>8}{'Rec':>8}{'F1':>8}{'AUC':>8}")
    for name, r in results.items():
        auc_str = f"{r['roc_auc']:.4f}" if r["roc_auc"] is not None else "  N/A"
        print(f"{name:<22}{r['accuracy']:>8.4f}{r['precision']:>8.4f}{r['recall']:>8.4f}{r['f1']:>8.4f}{auc_str:>8}")
        print(f"   Confusion matrix [[TN,FP],[FN,TP]]: {r['confusion_matrix']}")

    best = pick_best(results)
    print(f"\n>>> Model được chọn: {best}")

    out_dir = ROOT / "models" / "candidates"
    with open(out_dir / "eval_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "chosen_model": best}, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu {out_dir / 'eval_results.json'}")
