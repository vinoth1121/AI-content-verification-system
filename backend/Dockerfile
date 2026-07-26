# Backend Dockerfile — slim Python image with system deps for OpenCV / librosa
FROM python:3.12-slim AS base

# System deps for OpenCV headless + audio codecs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for layer caching
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code (backend + ai-engine)
COPY backend/ ./backend/
COPY ai-engine/ ./ai-engine/

WORKDIR /app/backend

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
