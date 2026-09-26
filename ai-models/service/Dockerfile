# Build context PHẢI là thư mục ai-models/ (xem docker-compose.yml: context: ./ai-models)
# để có thể COPY cả service/ lẫn models/ vào image.
FROM python:3.12-slim

WORKDIR /app

COPY service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service/main.py .
COPY models/model.joblib ./models/model.joblib
COPY models/metadata.json ./models/metadata.json
COPY models/schema.json ./models/schema.json

EXPOSE 8001

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
