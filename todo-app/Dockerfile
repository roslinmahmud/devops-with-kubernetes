# Angular build
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/todo/package*.json ./
RUN npm ci
COPY frontend/todo .
RUN npm run build --prod


FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/ ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=frontend-build /app/dist/todo/browser ./frontend

CMD ["python", "app.py"]