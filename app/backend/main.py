import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI(title="Mushroom Classification Backend")

# Cho phép Frontend gọi API nếu chạy khác cổng/domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lấy URL của AI Service từ biến môi trường trong docker-compose.yml
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

# Định nghĩa cấu trúc dữ liệu nhận từ Frontend (các đặc điểm hình thái học của nấm)
class MushroomFeatures(BaseModel):
    cap_shape: str
    cap_surface: str
    cap_color: str
    odor: str
    habitat: str

@app.get("/")
def read_root():
    return {"message": "Backend is running successfully!"}

@app.post("/predict")
async def predict_mushroom(features: MushroomFeatures):
    try:
        # Chuyển đổi dữ liệu sang dạng dict để gửi sang AI Service dưới dạng JSON
        payload = features.dict()
        
        # Gửi request sang AI Service
        response = requests.post(f"{AI_SERVICE_URL}/predict", json=payload)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error from AI Service")
            
        result = response.json()
        return result
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to AI Service: {str(e)}")