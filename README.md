# Phân loại nấm ăn được hay có độc (Mushroom Classification)

## 1. Thành viên
| Họ tên | MSSV | Phần việc |
|---|---|---|
| _Phạm Văn Tình_ | _10123316_ | Xây dựng cấu trúc dự án, Phân tích dữ liệu khám phá (EDA), Xây dựng AI Model, Xử lý Git & GitHub.|
| _Bùi Quang Trường_ | _10123333_ | Xây dựng Backend/Frontend (App), Viết tài liệu báo cáo, Kiểm thử hệ thống.|

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
_(sẽ cập nhật sau bước 3–4: huấn luyện ≥4 model + đánh giá)_

| Model | Metric chính (test) | Metric phụ | Train/Test time | Predict time | File size | Nhận xét |
|---|---|---|---|---|---|---|
| Baseline | | | | | | |
| Model 1 | | | | | | |
| Model 2 | | | | | | |
| Model 3 | | | | | | |
| Model 4 | | | | | | |

## 5. Đóng gói model
_(sẽ cập nhật sau bước 5.1)_ — dự kiến: `ai-models/models/model.joblib`, `schema.json`, `metadata.json`.

## 6. Kiến trúc hệ thống
```
[Frontend] → [Backend] → [AI Service] → (trả kết quả ngược lại)
                 ↓
             [MongoDB Atlas] (lưu lịch sử dự đoán)
```
_(sơ đồ chi tiết + giải thích luồng request_id sẽ bổ sung ở bước 5.2/5.6)_

## 7. Chạy trên máy
Yêu cầu: đã cài **Docker Desktop**.
```bash
cp .env.example .env
docker compose up --build
```
> ⚠️ Dockerfile của `ai-models/service`, `app/backend`, `app/frontend` đang được xây dựng — `docker compose up --build` sẽ hoạt động đầy đủ sau khi các thành phần này hoàn thiện (dự kiến trước 28/09/2026).

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
_(sẽ cập nhật ở bước 5.4)_

## 11. Demo online
_(sẽ cập nhật — địa chỉ App, địa chỉ AI Service/docs)_

## 12. Nhật ký đổi cổng/tunnel
| Thời điểm | Địa chỉ cũ | Địa chỉ mới |
|---|---|---|
| | | |

## 13. Kết quả kiểm thử hiệu năng
_(sẽ cập nhật ở bước 5.5)_

## 14. Hạn chế và hướng phát triển
_(sẽ cập nhật)_
