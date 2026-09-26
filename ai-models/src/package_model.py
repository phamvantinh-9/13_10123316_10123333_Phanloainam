"""
package_model.py — Bước 5.1: Đóng gói model cuối cùng.

Model được chọn ở Bước 4 (evaluate.py) đã là một sklearn Pipeline HOÀN CHỈNH
(gồm cả bước tiền xử lý 'prep' + bước phân loại 'clf'), nên đóng gói ở đây chỉ là
copy sang tên chuẩn model.joblib + ghi kèm metadata.json mô tả model.

AI Service (Bước 5.2) sẽ load đúng 2 file này (model.joblib + metadata.json) và
schema.json (đã có từ Bước 2) để biết cách validate input.
"""
import json
import platform
from datetime import datetime
from pathlib import Path

import joblib
import sklearn
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]  # ai-models/
MODELS_DIR = ROOT / "models"
CANDIDATES_DIR = MODELS_DIR / "candidates"


def package_final_model():
    eval_path = CANDIDATES_DIR / "eval_results.json"
    eval_data = json.load(open(eval_path, encoding="utf-8"))
    chosen_name = eval_data["chosen_model"]
    chosen_metrics = eval_data["results"][chosen_name]

    src_path = Path(chosen_metrics["model_path"])
    final_path = MODELS_DIR / "model.joblib"

    pipe = joblib.load(src_path)
    joblib.dump(pipe, final_path)
    file_size_kb = round(final_path.stat().st_size / 1024, 1)

    metadata = {
        "model_name": chosen_name,
        "model_version": "1.0.0",
        "trained_at": datetime.now().strftime("%Y-%m-%d"),
        "dataset": "Mushroom Classification (Kaggle uciml/mushroom-classification)",
        "n_train_samples": 6499,
        "n_test_samples": 1625,
        "test_metrics": {
            "accuracy": chosen_metrics["accuracy"],
            "precision": chosen_metrics["precision"],
            "recall": chosen_metrics["recall"],
            "f1": chosen_metrics["f1"],
            "roc_auc": chosen_metrics["roc_auc"],
        },
        "predict_time_ms": chosen_metrics["predict_time_ms"],
        "file_size_kb": file_size_kb,
        "library_versions": {
            "python": platform.python_version(),
            "scikit-learn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "joblib": joblib.__version__,
        },
        "pipeline_steps": [name for name, _ in pipe.steps],
        "label_map": {"e": 0, "p": 1},
        "label_names": {"0": "edible", "1": "poisonous"},
    }

    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Model được chọn: {chosen_name}")
    print(f"Đã lưu {final_path} ({file_size_kb} KB)")
    print(f"Đã lưu {MODELS_DIR / 'metadata.json'}")
    return metadata


if __name__ == "__main__":
    package_final_model()
