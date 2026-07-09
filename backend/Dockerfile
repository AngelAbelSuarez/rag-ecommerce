FROM python:3.13-slim

WORKDIR /app

# Dependencias primero (aprovecha caché de Docker)
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
