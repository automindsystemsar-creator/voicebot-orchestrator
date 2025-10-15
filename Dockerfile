FROM python:3.11-slim

# Evita prompts en instalaciones
ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY . .

# Railway inyecta $PORT; no pongas default con :-8000
CMD ["sh","-c","uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
