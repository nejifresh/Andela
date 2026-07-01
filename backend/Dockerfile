FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////data/cloudwaste.db \
    CORS_ORIGINS=http://localhost:3000

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /data \
    && chown -R app:app /data /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/sample_data ./sample_data
COPY backend/scripts ./scripts

USER app
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
