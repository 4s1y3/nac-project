FROM python:3.13-slim

WORKDIR /app

# Sistem bağımlılıkları (healthcheck için curl)
RUN apt-get update -q && apt-get install -y -q curl && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları önce kopyala (layer cache için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kaynak kodu kopyala
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
