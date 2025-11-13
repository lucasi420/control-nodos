from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# --- Configuración de conexión a la base de datos ---
DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Abre una conexión con la base de datos Neon"""
    return psycopg2.connect(DB_URL)

# --- Ruta principal ---
@app.route("/")
def home():
    return "✅ API funcionando correctamente - Proyecto Nodos"

# --- Ruta para probar conexión con Neon ---
@app.route("/testdb")
def testdb():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")  # Consulta simple para verificar conexión
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"status": "ok", "message": "Conectado a Neon", "timestamp": result[0]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Punto de entrada ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
