import os
# from sqlalchemy.pool import NullPool <--- ¡Esta línea se elimina!

class Config:
    # --- Configuración Estándar de Flask (Limpia) ---
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")
