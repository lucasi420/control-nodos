FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# 🚀 PASOS CRÍTICOS: Instalar dependencias de PostgreSQL a nivel de sistema
# 1. Instalar herramientas de compilación (gcc, build-essential)
# 2. Instalar el paquete de desarrollo de PostgreSQL (libpq-dev)
# 3. Limpiar los archivos temporales para mantener la imagen pequeña
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar requisitos primero
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código, incluyendo app.py, models.py, y init_db.py
COPY . .

# Puerto que usará Render
ENV PORT=10000

# 🌟 MODIFICACIÓN CRÍTICA: Inicializar DB y Luego Ejecutar Gunicorn
# Este comando hace dos cosas:
# 1. Ejecuta python init_db.py (Crea las tablas en Neon).
# 2. Si el paso anterior tiene éxito (&&), ejecuta gunicorn (Inicia el servidor web).
CMD python init_db.py && gunicorn --bind 0.0.0.0:$PORT app:app
