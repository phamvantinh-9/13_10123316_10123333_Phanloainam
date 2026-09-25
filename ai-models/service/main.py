from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="AI Model Service - Mushroom Classification")

# 1. Endpoint /health bắt buộc phục vụ cho Docker healthcheck trong docker-compose.yml
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def root():
    return {"message": "AI Service is running successfully"}

# Định dạng cấu trúc dữ liệu đầu vào nhận từ Backend (Khớp với các dropdown ở Frontend)
class MushroomInput(BaseModel):
    cap_shape: str
    cap_surface: str
    cap_color: str
    odor: str
    habitat: str

@app.post("/predict")
def predict(data: MushroomInput):
    try:
        # Sau này khi bạn train xong model học máy (ví dụ bằng scikit-learn lưu file .joblib),
        # bạn có thể load model và predict dựa trên các đặc điểm này tại đây.
        # Ví dụ:
        # features = [[data.cap_shape, data.cap_surface, data.cap_color, data.odor, data.habitat]]
        # prediction = model.predict(features)[0]

        # Tạm thời dùng logic giả lập để test toàn bộ luồng chạy thông suốt:
        # Nếu mùi hương là 'hôi thối' (foul) hoặc 'hăng cay' (pungent) thì dự đoán là Nấm độc, ngược lại là Nấm ăn được
        is_poisonous = data.odor in ["foul", "pungent", "fishy"]
        
        label = "Nấm Độc (Poisonous)" if is_poisonous else "Nấm Ăn Được (Edible)"
        confidence = 0.95 if is_poisonous else 0.88
        description = "Đặc điểm hình thái này cho thấy nấm có nguy cơ gây ngộ độc cao." if is_poisonous else "Đặc điểm lành tính, có thể sử dụng làm thực phẩm."

        return {
            "label": label,
            "confidence": confidence,
            "description": description
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))