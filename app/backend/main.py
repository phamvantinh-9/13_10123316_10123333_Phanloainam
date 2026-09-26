import logging
import os
import time
import uuid
from typing import Dict, List

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s backend %(message)s")
logger = logging.getLogger("backend")

app = FastAPI(title="Mushroom Classification Backend")

# Cho phép Frontend gọi API nếu chạy khác cổng/domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lấy URL của AI Service từ biến môi trường trong docker-compose.yml (KHÔNG hard-code localhost/IP)
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

APP_START_TIME = time.time()

# Lịch sử dự đoán lưu tạm trong RAM (nâng cấp sau: lưu MongoDB Atlas qua biến MONGODB_URI).
# Giới hạn 200 bản ghi gần nhất để tránh phình RAM khi demo lâu.
_history: List[dict] = []
_HISTORY_MAX = 200


class PredictPayload(BaseModel):
    # Dict tự do vì tên cột thật có dấu gạch ngang (vd "cap-shape"), không phải định danh Python hợp lệ.
    # Backend không tự giữ danh sách 21 cột cứng ở đây -> luôn khớp với schema.json thật ở AI Service,
    # tránh lặp lại danh sách cột ở 2 nơi rồi bị lệch nhau khi có thay đổi.
    features: Dict[str, str]


@app.get("/")
def read_root():
    return {"message": "Backend is running successfully!"}


@app.get("/health")
def health():
    ai_ok = False
    try:
        r = requests.get(f"{AI_SERVICE_URL}/health", timeout=3)
        ai_ok = r.status_code == 200
    except requests.exceptions.RequestException:
        ai_ok = False
    return {
        "status": "ok",
        "service": "backend",
        "uptime_seconds": round(time.time() - APP_START_TIME, 1),
        "ai_service_reachable": ai_ok,
    }


@app.get("/api/schema")
def get_schema():
    """Proxy schema.json từ AI Service để Frontend tự sinh form nhập liệu (21 thuộc tính)."""
    try:
        r = requests.get(f"{AI_SERVICE_URL}/schema", timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Không lấy được schema từ AI Service: {e}")


@app.post("/api/predict")
async def api_predict(payload: PredictPayload, request: Request):
    request_id = request.headers.get("x-request-id", uuid.uuid4().hex[:8])
    t0 = time.time()
    logger.info(f"req={request_id} nhan yeu cau du doan tu frontend")

    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/predict",
            json={"features": payload.features},
            headers={"x-request-id": request_id},
            timeout=10,
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"req={request_id} khong ket noi duoc AI Service: {e}")
        raise HTTPException(status_code=503, detail={"error": "ai_service_unreachable", "detail": str(e), "request_id": request_id})

    if response.status_code != 200:
        logger.info(f"req={request_id} AI Service tra loi loi {response.status_code}: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", response.text))

    result = response.json()
    elapsed_ms = round((time.time() - t0) * 1000, 2)
    logger.info(f"req={request_id} 200 OK total {elapsed_ms}ms prediction={result.get('prediction')}")

    # Lưu lịch sử (RAM) — mỗi bản ghi gồm input + kết quả để hiển thị lại ở trang lịch sử của FE
    _history.append({
        "request_id": request_id,
        "features": payload.features,
        "result": result,
        "timestamp": time.time(),
    })
    if len(_history) > _HISTORY_MAX:
        del _history[0]

    return result


@app.get("/api/history")
def api_history(limit: int = 20):
    return list(reversed(_history[-limit:]))


# Giữ endpoint /predict cũ (5 thuộc tính) để không phá vỡ các bản demo/test cũ nếu còn ai gọi trực tiếp.
# Bản demo chính thức của nhóm dùng /api/predict (đủ 21 thuộc tính) ở trên.
class LegacyMushroomFeatures(BaseModel):
    cap_shape: str
    cap_surface: str
    cap_color: str
    odor: str
    habitat: str


@app.post("/predict")
async def predict_mushroom_legacy(features: LegacyMushroomFeatures):
    raise HTTPException(
        status_code=410,
        detail="Endpoint /predict (5 thuoc tinh) da duoc thay bang /api/predict (du 21 thuoc tinh). "
               "Vui long goi POST /api/predict voi body {'features': {...21 khoa...}}.",
    )
