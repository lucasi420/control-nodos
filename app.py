from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Configuración de conexión a Neon (usa variables de entorno de Render)
DB_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DB_URL)

@app.route('/')
def home():
    return '✅ API funcionando correctamente - Proyecto Nodos'

# Obtener todos los nodos
@app.route('/nodos', methods=['GET'])
def obtener_nodos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT nodo FROM datos ORDER BY nodo;")
    nodos = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(nodos)

# Obtener datos por nodo
@app.route('/nodo/<string:nodo>', methods=['GET'])
def obtener_datos_nodo(nodo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT placa, puerto, bandwidth_up, bandwidth_down, tecnico, fecha
        FROM datos
        WHERE nodo = %s
        ORDER BY placa, puerto;
    """, (nodo,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = [
        {
            "placa": r[0],
            "puerto": r[1],
            "bandwidth_up": r[2],
            "bandwidth_down": r[3],
            "tecnico": r[4],
            "fecha": r[5].strftime("%Y-%m-%d %H:%M:%S") if r[5] else None
        } for r in rows
    ]
    return jsonify(data)

# Guardar o actualizar bandwidth
@app.route('/guardar', methods=['POST'])
def guardar_bandwidth():
    data = request.json
    nodo = data.get("nodo")
    placa = data.get("placa")
    puerto = data.get("puerto")
    up = data.get("bandwidth_up")
    down = data.get("bandwidth_down")
    tecnico = data.get("tecnico")
    fecha = datetime.now()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE datos
        SET bandwidth_up = %s,
            bandwidth_down = %s,
            tecnico = %s,
            fecha = %s
        WHERE nodo = %s AND placa = %s AND puerto = %s;
    """, (up, down, tecnico, fecha, nodo, placa, puerto))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "ok", "message": "Datos guardados correctamente ✅"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
