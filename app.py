from flask import Flask, request, jsonify
import psycopg2
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Datos de conexión a Neon (vas a copiar tu string real más abajo)
DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DB_URL)

@app.route("/nodos", methods=["GET"])
def get_nodos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM nodos ORDER BY id DESC;")
    data = cur.fetchall()
    cur.close()
    conn.close()

    nodos = [
        {
            "id": r[0],
            "nodo": r[1],
            "placa": r[2],
            "puerto": r[3],
            "bandwidth_up": r[4],
            "bandwidth_down": r[5],
            "tecnico": r[6],
            "fecha": r[7].strftime("%Y-%m-%d %H:%M")
        }
        for r in data
    ]
    return jsonify(nodos)

@app.route("/nodos", methods=["POST"])
def add_nodo():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO nodos (nodo, placa, puerto, bandwidth_up, bandwidth_down, tecnico, fecha)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data["nodo"],
        data.get("placa"),
        data.get("puerto"),
        data.get("bandwidth_up"),
        data.get("bandwidth_down"),
        data.get("tecnico"),
        datetime.now()
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Registro guardado correctamente"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
