# Phân loại nấm ăn được hay có độc (Mushroom Classification)



## 1. Thành viên
| Họ tên | MSSV | Phần việc |
|---|---|---|
| Phạm Văn Tình |10123316 | |
| Bùi Quang Trường |10123333 | |

## 2. Bài toán
- **Mô tả:** Dự đoán một cây nấm là **ăn được** hay **có độc** dựa trên các đặc điểm hình thái quan sát được (hình dạng/màu mũ nấm, mùi, màu phiến nấm, môi trường sống, v.v.).
- **Loại bài toán:** Phân loại nhị phân (binary classification).
- **Cột mục tiêu:** `class` (`e` = edible / ăn được, `p` = poisonous / độc).
- **Ý nghĩa thực tế:** Hỗ trợ cảnh báo sớm nguy cơ ngộ độc nấm dựa trên đặc điểm dễ quan sát bằng mắt thường, trước khi sử dụng.

## 3. Dữ liệu
- **Nguồn:** [Kaggle – Mushroom Classification](https://www.kaggle.com/datasets/uciml/mushroom-classification) (gốc từ UCI Machine Learning Repository).
- **Giấy phép:** Public Domain / CC0.
- **Quy mô:** 8.124 mẫu, 22 thuộc tính categorical + 1 nhãn.
- **Chi tiết cột & cách giải nén:** xem [`ai-models/data/DATA.md`](ai-models/data/DATA.md).

## 4. Kết quả model
Đánh giá trên tập test (1.625 mẫu, chưa từng dùng để train/tune). Chi tiết đầy đủ + confusion matrix xem `docs/baocao.docx` mục 5.

| Model | Accuracy | Precision | Recall | F1 | Train time | Predict time | File size | Nhận xét |
|---|---|---|---|---|---|---|---|---|
| Baseline (Dummy) | 0.5182 | 0.0000 | 0.0000 | 0.0000 | 0,02s | 4,1ms | 7,4KB | Luôn đoán lớp đông hơn |
| **Logistic Regression** ✅ | **1.0000** | **1.0000** | **1.0000** | **1.0000** | 0,88s | **3,68ms** | **8,5KB** | **Model được chọn** — nhanh & nhẹ nhất |
| KNN | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6,97s | 5,1ms | 1.683,3KB | File nặng nhất (lưu cả tập train) |
| Random Forest | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 13,92s | 8,4ms | 561,8KB | |
| SVM | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 53,59s | 4,1ms | 66,8KB | Train lâu nhất |

## 5. Đóng gói model
- `ai-models/models/model.joblib` — Logistic Regression + tiền xử lý One-Hot đóng gói chung (1 sklearn Pipeline hoàn chỉnh).
- `ai-models/models/metadata.json` — tên/phiên bản model, chỉ số test, phiên bản thư viện lúc train (scikit-learn 1.8.0, pandas 3.0.2, numpy 2.4.4).
- `ai-models/models/schema.json` — 21 thuộc tính + giá trị hợp lệ + ánh xạ nhãn (từ Bước 2).
- Cách xuất từ Colab: chạy tuần tự `01_eda → 02_preprocess → 03_train → 04_evaluate` rồi `python ai-models/src/package_model.py`, commit `model.joblib` + `metadata.json` vào Git — Dockerfile AI Service tự COPY khi build.

## 6. Kiến trúc hệ thống
```
[Frontend :80] --/api/*--> [Backend :8000] --/predict--> [AI Service :8001]
   (React+Vite,               (FastAPI,                    (FastAPI + model.joblib
    Nginx proxy)             forward + lưu lịch sử)          nạp sẵn khi start)
```
- Frontend tự sinh form 21 thuộc tính bằng cách gọi `GET /api/schema` (Backend proxy từ AI Service `GET /schema`) — không hard-code danh sách cột ở Frontend.
- Mỗi request có 1 `request_id` xuyên suốt 3 service để log/debug (xem mục 12 và `docs/baocao.docx` mục 7.2).
- Chi tiết đặc tả API đầy đủ: xem `docs/baocao.docx` mục 7.3.

## 7. Chạy trên máy
Yêu cầu: đã cài **Docker Desktop**.
```bash
cp .env.example .env
docker compose up --build
```
Sau khi chạy xong: mở `http://localhost:3000` (Frontend), `http://localhost:8000/health` (Backend), `http://localhost:8001/health` (AI Service).

## 8. Huấn luyện lại model
_(sẽ cập nhật: link Colab, thứ tự chạy notebook `01_eda → 02_preprocess → 03_train → 04_evaluate`)_

## 9. Biến môi trường
| Biến | Ý nghĩa |
|---|---|
| `AI_SERVICE_PORT` | Cổng chạy AI Service |
| `BACKEND_PORT` | Cổng chạy Backend |
| `FRONTEND_PORT` | Cổng chạy Frontend |
| `AI_SERVICE_URL` | Địa chỉ Backend gọi tới AI Service (tên service khi local, link public/tunnel khi deploy) |
| `MONGODB_URI` | Chuỗi kết nối MongoDB Atlas |
| `API_URL` | Địa chỉ Frontend gọi tới Backend |

## 10. Triển khai
Xem hướng dẫn chi tiết từng bước (2 phương án: máy cá nhân + ngrok, hoặc Render) tại [`docs/HUONG_DAN_TRIEN_KHAI.md`](docs/HUONG_DAN_TRIEN_KHAI.md).

## 11. Demo online
- Địa chỉ App: https://squiggly-breeding-negligent.ngrok-free.dev/
- Địa chỉ AI Service: _(nếu public riêng)_

## 12. Nhật ký đổi cổng/tunnel
| Thời điểm | Địa chỉ cũ | Địa chỉ mới |
|---|---|---|
|25/09/2026 | Localhost| https://squiggly-breeding-negligent.ngrok-free.dev/|

## 13. Kết quả kiểm thử hiệu năng
Chạy kiểm tra tải bằng script tự viết (không cần cài k6/Locust):
```bash
python ai-models/service/tests/load_test.py --url <địa-chỉ-public>/predict --users 15 --duration 60
```
Kết quả đo được (điền sau khi chạy trên hệ thống đã public):

| Chỉ số | Giá trị |
|---|---|
| Request/giây (RPS) |~24.17 req/s |
| Tỉ lệ lỗi |0% |
| p50 |~115.0 ms |
| p95 |~195.4 ms |

## 14. Hạn chế và hướng phát triển
**Hạn chế:**
- Bộ dữ liệu có độ tách biệt giữa 2 lớp rất cao (gần hoàn hảo) — dữ liệu thực tế thường nhiễu và khó phân loại hơn.
- Lịch sử dự đoán hiện lưu tạm RAM ở Backend, chưa nối MongoDB Atlas thật.
- Form 21 thuộc tính đòi hỏi người dùng hiểu thuật ngữ sinh học.

**Hướng phát triển:**
- Kết nối MongoDB Atlas thật để lưu lịch sử lâu dài.
- Thêm ảnh minh hoạ cho từng giá trị thuộc tính trên Frontend.
- Thử thêm mô hình Gradient Boosting/XGBoost; mở rộng sang nhận diện qua ảnh chụp thực tế (Computer Vision).
