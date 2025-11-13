from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- Configuración de conexión ---
DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DB_URL)

# --- Ruta principal ---
@app.route("/")
def home():
    return render_template("index.html")

# --- Test de conexión ---
@app.route("/testdb")
def testdb():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"status": "ok", "message": "Conectado a Neon", "timestamp": result[0]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# === CRUD DE NODOS ===

# 📋 Obtener todos los nodos
@app.route("/nodos", methods=["GET"])
def get_nodos():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nodo, placa, puerto, bandwidth_up, bandwidth_down, tecnico, fecha
            FROM nodos
            ORDER BY nodo ASC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        nodos = []
        for row in rows:
            nodos.append({
                "id": row[0],
                "nodo": row[1],
                "placa": row[2],
                "puerto": row[3],
                "bandwidth_up": row[4],
                "bandwidth_down": row[5],
                "tecnico": row[6],
                "fecha": row[7]
            })
        return jsonify(nodos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ➕ Agregar un nuevo nodo
@app.route("/nodos", methods=["POST"])
def add_nodo():
    data = request.json
    nodo = data.get("nodo")
    placa = data.get("placa")
    puerto = data.get("puerto")

    if not nodo:
        return jsonify({"error": "El campo 'nodo' es obligatorio"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO nodos (nodo, placa, puerto)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (nodo, placa, puerto))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Nodo agregado correctamente", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✏️ Editar bandwidth y técnico
@app.route("/nodos/<int:id>", methods=["PUT"])
def update_nodo(id):
    data = request.json
    up = data.get("bandwidth_up")
    down = data.get("bandwidth_down")
    tecnico = data.get("tecnico")
    fecha = datetime.now()

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE nodos
            SET bandwidth_up = %s,
                bandwidth_down = %s,
                tecnico = %s,
                fecha = %s
            WHERE id = %s;
        """, (up, down, tecnico, fecha, id))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Nodo actualizado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Ejecución ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
