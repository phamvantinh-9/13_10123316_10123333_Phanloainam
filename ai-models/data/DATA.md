# DATA.md — Mô tả bộ dữ liệu

## Nguồn
- **Tên bộ dữ liệu:** Mushroom Classification
- **Nguồn gốc:** UCI Machine Learning Repository — "Mushroom Database" (1987), được đăng lại trên Kaggle tại `uciml/mushroom-classification`.
- **Giấy phép:** Public Domain / CC0 (dữ liệu gốc từ UCI, không giới hạn sử dụng cho mục đích học thuật).
- **Số dòng:** 8.124 mẫu nấm.
- **Số cột:** 23 (1 cột nhãn `class` + 22 thuộc tính mô tả đặc điểm hình thái).

## Loại bài toán
Phân loại nhị phân (binary classification): dự đoán một cây nấm là **ăn được (edible, `e`)** hay **độc (poisonous, `p`)** dựa trên các đặc điểm quan sát được (hình dạng mũ nấm, màu sắc, mùi, v.v.).

## Cột mục tiêu
- `class`: `e` = edible (ăn được), `p` = poisonous (độc, bao gồm cả loại độc tính chưa xác định rõ).

## Danh sách 22 thuộc tính đầu vào (toàn bộ là dữ liệu phân loại — categorical)
| Cột | Ý nghĩa |
|---|---|
| cap-shape | Hình dạng mũ nấm |
| cap-surface | Bề mặt mũ nấm |
| cap-color | Màu mũ nấm |
| bruises | Có vết bầm/dập khi chạm không |
| odor | Mùi |
| gill-attachment | Cách phiến nấm gắn vào cuống |
| gill-spacing | Khoảng cách giữa các phiến nấm |
| gill-size | Kích thước phiến nấm |
| gill-color | Màu phiến nấm |
| stalk-shape | Hình dạng cuống nấm |
| stalk-root | Dạng rễ/gốc cuống |
| stalk-surface-above-ring | Bề mặt cuống phía trên vòng |
| stalk-surface-below-ring | Bề mặt cuống phía dưới vòng |
| stalk-color-above-ring | Màu cuống phía trên vòng |
| stalk-color-below-ring | Màu cuống phía dưới vòng |
| veil-type | Loại màng bao |
| veil-color | Màu màng bao |
| ring-number | Số lượng vòng trên cuống |
| ring-type | Loại vòng |
| spore-print-color | Màu bào tử in |
| population | Mật độ quần thể xuất hiện |
| habitat | Môi trường sống |

> Toàn bộ giá trị được mã hóa bằng 1 ký tự viết tắt (ví dụ `cap-shape`: `b`=bell, `c`=conical, `x`=convex, `f`=flat, `k`=knobbed, `s`=sunken). Bảng giải mã đầy đủ từng ký tự sẽ được trình bày trong notebook EDA (`ai-models/colab/01_eda`) và báo cáo.

## Cách giải nén
```bash
cd ai-models/data
unzip dataset.zip        # ra file mushrooms.csv (8.124 dòng, có header)
```

## Ghi chú
- Không có giá trị số (numeric) — toàn bộ pipeline tiền xử lý sẽ dùng mã hóa phân loại (One-Hot / Ordinal), không cần chuẩn hóa StandardScaler cho các mô hình dựa trên cây.
- Cột `veil-type` chỉ có duy nhất 1 giá trị trong toàn bộ tập dữ liệu → sẽ được loại bỏ ở bước xử lý dữ liệu (không mang thông tin phân biệt).
- Cột `stalk-root` có giá trị thiếu (`?`) → cần xử lý ở bước làm sạch dữ liệu.
