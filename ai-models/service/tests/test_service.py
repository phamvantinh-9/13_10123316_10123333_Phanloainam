"""
Test cho AI Service. Chạy: cd ai-models/service && pytest
(cần có models/model.joblib, models/metadata.json, models/schema.json cùng thư mục — copy từ ai-models/models/)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from main import app, FEATURE_NAMES, ALLOWED_VALUES

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_model_info():
    r = client.get("/model-info")
    assert r.status_code == 200
    assert "model_name" in r.json()


def test_schema():
    r = client.get("/schema")
    assert r.status_code == 200
    assert "features" in r.json()


def _valid_sample():
    return {col: sorted(ALLOWED_VALUES[col])[0] for col in FEATURE_NAMES}


def test_predict_valid_input():
    r = client.post("/predict", json={"features": _valid_sample()})
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] in ("edible", "poisonous")
    assert 0 <= body["probability"] <= 1
    assert "request_id" in body


def test_predict_missing_field():
    sample = _valid_sample()
    removed_key = next(iter(sample))
    del sample[removed_key]
    r = client.post("/predict", json={"features": sample})
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "invalid_input"


def test_predict_invalid_value():
    sample = _valid_sample()
    first_key = next(iter(sample))
    sample[first_key] = "___gia_tri_khong_ton_tai___"
    r = client.post("/predict", json={"features": sample})
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "invalid_input"
