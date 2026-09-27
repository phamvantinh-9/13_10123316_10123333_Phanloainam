# Hướng dẫn Triển khai Public (Bước 5.4)

Có 2 cách được thầy chấp nhận. Chọn 1 trong 2 — không cần làm cả hai.

---
## Cách A — Chạy trên máy cá nhân + ngrok (khuyến nghị, nhanh nhất, làm được ngay hôm nay)

### A.1. Chuẩn bị
1. Tài khoản ngrok miễn phí: https://ngrok.com/ → Sign up → lấy **Authtoken** ở trang Dashboard.
2. Tải ngrok: https://ngrok.com/download (hoặc `choco install ngrok` trên Windows nếu có Chocolatey).
3. Cài authtoken (chạy 1 lần):
   ```bash
   ngrok config add-authtoken <token-cua-ban>
   ```

### A.2. Chạy hệ thống local như bình thường
```bash
docker compose up --build
```
Đảm bảo `http://localhost:3000` chạy được trước khi sang bước tiếp theo.

### A.3. Mở đường hầm cho Frontend
Mở **1 cửa sổ terminal MỚI** (không tắt cửa sổ đang chạy docker), chạy:
```bash
ngrok http 3000
```
Ngrok sẽ hiện ra 1 dòng dạng:
```
Forwarding    https://ab12-14-241-x-x.ngrok-free.app -> http://localhost:3000
```
→ Đây chính là **địa chỉ App công khai**. Copy lại link này.

Nếu muốn AI Service cũng public riêng (không bắt buộc nếu Backend/Frontend đã chạy nội bộ qua Docker network): mở thêm 1 terminal khác, chạy `ngrok http 8001`.

### A.4. Cập nhật lại README
- Không cần đổi `AI_SERVICE_URL` trong `.env` (Backend vẫn gọi AI Service qua tên service nội bộ `http://ai-service:8001`).
- Ghi địa chỉ ngrok vào `README.md` mục 11 "Demo online".
- **Lưu ý quan trọng**: bản ngrok miễn phí đổi sang link MỚI mỗi lần tắt/bật lại `ngrok http 3000`. Theo đúng yêu cầu của thầy:
  - Mỗi lần link đổi → ghi vào `README.md` mục 12 "Nhật ký đổi cổng/tunnel" (thời điểm đổi + link cũ → link mới).
  - Không có gói ngrok trả phí (không có domain cố định) → **mỗi sáng thứ Hai phải mở lại ngrok, lấy link mới, cập nhật README** đến ngày bảo vệ.
  - Trước ngày bảo vệ 10-15 phút: mở lại `docker compose up` + `ngrok http 3000`, kiểm tra link còn chạy.

### A.5. Kiểm tra
Mở link ngrok trên **trình duyệt ở điện thoại hoặc máy khác** (không phải máy đang chạy Docker) để chắc chắn người khác truy cập được thật.

---
## Cách B — Deploy lên Render (cloud, có địa chỉ cố định, không lo đổi link)

### B.1. Chuẩn bị
1. Tài khoản Render miễn phí: https://render.com (đăng nhập bằng GitHub cho tiện).
2. Repo phải đã **Public** trên GitHub.

### B.2. Deploy AI Service
1. Render Dashboard → **New** → **Web Service**.
2. Chọn repo GitHub của bạn.
3. Cấu hình:
   - **Root Directory**: `ai-models`
   - **Environment**: Docker
   - **Dockerfile Path**: `service/Dockerfile`
4. Bấm **Create Web Service**, đợi build xong (vài phút). Render cho 1 địa chỉ dạng `https://ten-nhom-ai-service.onrender.com`.

### B.3. Deploy Backend
1. **New** → **Web Service** → cùng repo.
2. Cấu hình:
   - **Root Directory**: `app/backend`
   - **Environment**: Docker
3. Tab **Environment**, thêm biến:
   - `AI_SERVICE_URL` = địa chỉ AI Service ở bước B.2
4. Create Web Service, đợi build xong → có địa chỉ Backend, ví dụ `https://ten-nhom-backend.onrender.com`.

### B.4. Deploy Frontend
1. **New** → **Static Site**.
2. Root Directory: `app/frontend`.
3. Build Command: `npm install && npm run build`, Publish Directory: `dist`.
4. **Quan trọng**: Frontend hiện gọi `/api/...` (proxy qua Nginx tới `backend:8000`, chỉ chạy nội bộ trong docker-compose). Khi deploy tách rời trên Render, cần sửa `App.jsx` gọi thẳng URL đầy đủ của Backend thay vì đường dẫn tương đối. Báo tôi nếu chọn Cách B, tôi sẽ chỉnh `App.jsx` cho phù hợp (thêm biến `VITE_API_URL`).

### B.5. Lưu ý về gói miễn phí Render
- Gói free sẽ **"ngủ"** sau ~15 phút không có traffic → lần gọi đầu tiên sau khi ngủ sẽ chậm (10-30 giây "đánh thức"). **Vào trước web 5-10 phút trước khi thầy kiểm tra/bảo vệ** để "làm nóng" hệ thống.
- Địa chỉ Render KHÔNG đổi qua các lần deploy lại → không cần ghi nhật ký đổi link mỗi tuần như Cách A.

---
## Sau khi chọn xong 1 trong 2 cách — cập nhật các chỗ sau
1. `README.md` mục 11 "Demo online": điền địa chỉ App + AI Service thật.
2. `docs/slide.pptx` slide 12 "Demo & Triển khai": điền địa chỉ vào chỗ `__________________`.
3. `docs/baocao.docx` mục 8 "Triển khai": mô tả cách đã chọn (A hoặc B) + địa chỉ.
4. Chạy thử kiểm tra tải nhắm vào địa chỉ PUBLIC (không phải localhost):
   ```bash
   python ai-models/service/tests/load_test.py --url <địa-chỉ-public>/predict --users 15 --duration 60
   ```
5. Commit + push.
