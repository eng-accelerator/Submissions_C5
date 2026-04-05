# Coolify: set **Base Directory** to `backend` (or Dockerfile path `backend/Dockerfile`).
# Configure **runtime** environment variables (see `.env.example`). Required at minimum:
#   CORS_ALLOWED_ORIGINS — comma-separated origins, e.g. https://outskill.tulsi-vatika.com
# Plus Supabase, LLM keys, etc. as needed.

FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request; p=os.environ.get('PORT','8000'); urllib.request.urlopen(f'http://127.0.0.1:{p}/health')" || exit 1

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
