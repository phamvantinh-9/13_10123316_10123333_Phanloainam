# Stage 1: Build ứng dụng React bằng Vite
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Chạy production bằng Nginx
FROM nginx:alpine
# Copy kết quả build từ Vite (thư mục dist) vào thư mục public của Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy file cấu hình Nginx để xử lý định tuyến (proxy /predict sang backend)
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]