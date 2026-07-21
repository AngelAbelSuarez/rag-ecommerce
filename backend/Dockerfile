FROM python:3.13-slim

WORKDIR /app

# Dependencias primero (aprovecha caché de Docker)
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
