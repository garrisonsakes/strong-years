# Build from the rebuild/ root so the spec files ship with the image:
#   docker build -f workers/Dockerfile -t changsun-workers .
FROM python:3.11-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg tesseract-ocr tesseract-ocr-eng ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY workers/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY workers/ /app/
# Spec inputs the gates read at runtime (SAFETY_RULES.md is authoritative; blocked_claims.json + prompts/03 for the judge)
COPY SAFETY_RULES.md EVIDENCE.md n8n_core_workflow.json /app/spec/
COPY prompts/ /app/spec/prompts/

ENV SPEC_DIR=/app/spec \
    OUTPUT_DIR=/data/out \
    WORK_DIR=/data/work \
    X264_PRESET=medium \
    PYTHONUNBUFFERED=1
VOLUME ["/data"]
# WORKER_TOKEN must be provided at runtime (fail closed: 503 without it). Optional: FETCH_ALLOWED_HOSTS, C2PA_SIGN_CERT/KEY.
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8080/health')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
