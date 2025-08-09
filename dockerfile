# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY main.py .
COPY static/ static/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--port", "8000"]