"""
AI Service — nạp model.joblib (đã gồm cả tiền xử lý + model) NGAY KHI KHỞI ĐỘNG container,
nhận đặc điểm nấm, trả về dự đoán ăn được/độc.

Endpoints:
  GET  /health      -> trạng thái service, thời gian đã chạy
  GET  /model-info   -> thông tin model đang chạy (metadata.json)
  GET  /schema        -> schema.json (BE/FE dùng để validate & build form)
  POST /predict        -> {"features": {...21 thuộc tính...}} -> dự đoán
"""
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Dict

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s ai-service %(message)s")
logger = logging.getLogger("ai-service")

APP_START_TIME = time.time()
MODELS_DIR = Path(__file__).resolve().parent / "models"

app = FastAPI(title="Mushroom Classification - AI Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== NẠP MODEL NGAY KHI KHỞI ĐỘNG CONTAINER (không tải lại mỗi request) ======
MODEL_PATH = MODELS_DIR / "model.joblib"
METADATA_PATH = MODELS_DIR / "metadata.json"
SCHEMA_PATH = MODELS_DIR / "schema.json"

logger.info(f"Đang nạp model từ {MODEL_PATH} ...")
model_pipeline = joblib.load(MODEL_PATH)
metadata = json.load(open(METADATA_PATH, encoding="utf-8"))
schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
FEATURE_NAMES = [f["name"] for f in schema["features"]]
ALLOWED_VALUES = {f["name"]: set(f["allowed_values"]) for f in schema["features"]}
LABEL_NAMES = schema["target"]["labels_full_name"]  # {"e": "edible", "p": "poisonous"}
# model output 0/1 -> "e"/"p" -> tên đầy đủ
CODE_BY_INT = {v: k for k, v in schema["target"]["encoding"].items()}  # {0:"e", 1:"p"}
logger.info(f"Đã nạp xong model '{metadata['model_name']}' v{metadata['model_version']} "
            f"({len(FEATURE_NAMES)} thuộc tính đầu vào)")


class PredictRequest(BaseModel):
    features: Dict[str, str]


def validate_features(features: dict) -> None:
    missing = [c for c in FEATURE_NAMES if c not in features]
    if missing:
        raise ValueError(f"Thiếu thuộc tính: {missing}")
    extra = [c for c in features if c not in FEATURE_NAMES]
    if extra:
        raise ValueError(f"Thuộc tính không xác định (không có trong schema): {extra}")
    for col, val in features.items():
        if val not in ALLOWED_VALUES[col]:
            raise ValueError(
                f"Giá trị '{val}' không hợp lệ cho '{col}'. "
                f"Giá trị hợp lệ: {sorted(ALLOWED_VALUES[col])}"
            )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-service",
        "port": 8001,
        "uptime_seconds": round(time.time() - APP_START_TIME, 1),
        "model_loaded": model_pipeline is not None,
    }


@app.get("/model-info")
def model_info():
    return metadata


@app.get("/schema")
def get_schema():
    return schema


@app.post("/predict")
def predict(payload: PredictRequest, request: Request):
    request_id = request.headers.get("x-request-id", uuid.uuid4().hex[:8])
    t0 = time.time()
    try:
        validate_features(payload.features)
    except ValueError as e:
        logger.info(f"req={request_id} invalid_input: {e}")
        raise HTTPException(status_code=400, detail={"error": "invalid_input", "detail": str(e), "request_id": request_id})

    # Sắp xếp đúng thứ tự cột theo schema trước khi đưa vào pipeline
    row = {col: payload.features[col] for col in FEATURE_NAMES}
    X = pd.DataFrame([row])

    pred_int = int(model_pipeline.predict(X)[0])
    try:
        proba = float(model_pipeline.predict_proba(X)[0][pred_int])
    except Exception:
        proba = None

    pred_code = CODE_BY_INT[pred_int]           # "e" hoặc "p"
    pred_label = LABEL_NAMES[pred_code]          # "edible" hoặc "poisonous"

    elapsed_ms = round((time.time() - t0) * 1000, 2)
    logger.info(f"req={request_id} predict {pred_label} p={proba} model={metadata['model_version']} in {elapsed_ms}ms")

    return {
        "prediction": pred_label,
        "probability": round(proba, 4) if proba is not None else None,
        "model_version": metadata["model_version"],
        "model_name": metadata["model_name"],
        "request_id": request_id,
    }
