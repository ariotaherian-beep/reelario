FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend

RUN mkdir -p /app/storage/uploads \
             /app/storage/projects \
             /app/storage/previews \
             /app/storage/renders

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

EXPOSE 10000

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
