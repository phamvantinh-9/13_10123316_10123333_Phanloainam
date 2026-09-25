"""
preprocess.py — Tiền xử lý dữ liệu cho bài toán Phân loại nấm ăn được hay có độc.

Dùng chung ở 3 nơi:
  - ai-models/colab/02_preprocess.ipynb (khám phá & kiểm tra bước tiền xử lý)
  - ai-models/colab/03_train.ipynb (huấn luyện model, ghép chung với ColumnTransformer này thành 1 Pipeline)
  - ai-models/service/ (AI Service load lại model.joblib đã chứa pipeline này bên trong, KHÔNG viết lại tay ở BE)
"""
import json
import zipfile
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

TARGET_COL = "class"
DROP_COLS = ["veil-type"]          # cột hằng số, không mang thông tin (xem EDA - Hình 1.4)
MISSING_TOKEN = "?"                 # ký hiệu giá trị thiếu gốc trong dataset (chỉ có ở stalk-root)


def load_raw_data(zip_path: str) -> pd.DataFrame:
    """Đọc trực tiếp mushrooms.csv từ dataset.zip, không cần giải nén ra đĩa."""
    with zipfile.ZipFile(zip_path) as z:
        with z.open("mushrooms.csv") as f:
            df = pd.read_csv(f)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Làm sạch dữ liệu theo quyết định đã chốt ở bước EDA:
      - Loại cột veil-type (hằng số).
      - Giữ nguyên ký hiệu '?' ở stalk-root, coi như MỘT MỨC PHÂN LOẠI RIÊNG
        (không xoá dòng, không điền mode) — Word/sklearn OneHotEncoder sẽ tự
        sinh ra 1 cột nhị phân riêng cho giá trị '?' này.
    """
    df = df.copy()
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])
    # Không cần xử lý gì thêm cho '?': OneHotEncoder ở bước sau sẽ tự coi nó
    # là 1 category bình thường của cột stalk-root.
    return df


def get_feature_columns(df: pd.DataFrame) -> list:
    return [c for c in df.columns if c != TARGET_COL]


def build_preprocessor(feature_cols: list) -> ColumnTransformer:
    """
    Toàn bộ feature đều là categorical -> OneHotEncoder duy nhất.
    handle_unknown='ignore' để AI Service không bị lỗi nếu sau này gặp
    giá trị lạ chưa từng thấy lúc huấn luyện (an toàn khi lên production).
    """
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), feature_cols),
        ]
    )


def encode_target(df: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Mã hoá cột class: e=0 (edible), p=1 (poisonous). Trả về y và bảng ánh xạ."""
    mapping = {"e": 0, "p": 1}
    y = df[TARGET_COL].map(mapping)
    return y, mapping


def build_schema(df_before_drop: pd.DataFrame, feature_cols: list, label_mapping: dict) -> dict:
    """Sinh schema.json — hợp đồng dữ liệu dùng chung giữa EDA, huấn luyện, BE (validate) và FE (form)."""
    schema = {
        "target": {
            "column": TARGET_COL,
            "encoding": label_mapping,
            "labels_full_name": {"e": "edible", "p": "poisonous"},
        },
        "dropped_columns": DROP_COLS,
        "missing_value_token": MISSING_TOKEN,
        "missing_value_strategy": "Giữ nguyên làm 1 category riêng (áp dụng cho stalk-root), không xoá dòng, không điền mode.",
        "features": [],
    }
    for col in feature_cols:
        schema["features"].append({
            "name": col,
            "type": "categorical",
            "allowed_values": sorted(df_before_drop[col].astype(str).unique().tolist()),
        })
    return schema


def split(df: pd.DataFrame, feature_cols: list, y: pd.Series, test_size=0.2, random_state=42):
    X = df[feature_cols]
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


if __name__ == "__main__":
    # Chạy thử toàn bộ pipeline tiền xử lý + in kết quả kiểm tra (dùng cho báo cáo / notebook)
    import joblib

    ROOT = Path(__file__).resolve().parents[1]  # ai-models/
    df_raw = load_raw_data(str(ROOT / "data" / "dataset.zip"))
    print(f"Dữ liệu gốc: {df_raw.shape[0]} dòng, {df_raw.shape[1]} cột")

    df_clean = clean_data(df_raw)
    print(f"Sau khi loại veil-type: {df_clean.shape[0]} dòng, {df_clean.shape[1]} cột")

    feature_cols = get_feature_columns(df_clean)
    y, mapping = encode_target(df_clean)
    print(f"Mã hoá nhãn: {mapping}")
    print(f"Phân bố nhãn sau mã hoá:\n{y.value_counts()}")

    X_train, X_test, y_train, y_test = split(df_clean, feature_cols, y)
    print(f"Train: {X_train.shape[0]} mẫu | Test: {X_test.shape[0]} mẫu")
    print(f"Tỷ lệ nhãn train:\n{y_train.value_counts(normalize=True)}")
    print(f"Tỷ lệ nhãn test:\n{y_test.value_counts(normalize=True)}")

    pre = build_preprocessor(feature_cols)
    X_train_enc = pre.fit_transform(X_train)
    X_test_enc = pre.transform(X_test)
    print(f"Số chiều sau One-Hot Encoding: {X_train_enc.shape[1]} cột (từ {len(feature_cols)} thuộc tính gốc)")

    schema = build_schema(df_clean, feature_cols, mapping)
    models_dir = ROOT / "models"
    models_dir.mkdir(exist_ok=True)
    with open(models_dir / "schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu {models_dir / 'schema.json'}")

    joblib.dump(pre, models_dir / "preprocessor.joblib")
    print(f"Đã lưu {models_dir / 'preprocessor.joblib'} "
          f"(sẽ được ghép chung với model đã chọn thành model.joblib ở Bước 5.1)")
