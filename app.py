from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- Configuración de conexión ---
# DB_URL se obtiene de las variables de entorno, asumiendo una conexión segura.
DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Establece la conexión a la base de datos PostgreSQL."""
    # Nota: Es crucial que la variable de entorno DATABASE_URL esté configurada.
    return psycopg2.connect(DB_URL)

# --- Ruta principal ---
@app.route("/")
def home():
    """Renderiza la plantilla principal del frontend."""
    return render_template("index.html")

# --- Test de conexión ---
@app.route("/testdb")
def testdb():
    """Verifica la conexión a la base de datos."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"status": "ok", "message": "Conectado a Neon", "timestamp": result[0]})
    except Exception as e:
        # En caso de error, devuelve un mensaje claro
        return jsonify({"status": "error", "message": f"Error de conexión: {str(e)}"}), 500


# === CRUD DE NODOS ===

# 📋 Obtener todos los nodos
@app.route("/nodos", methods=["GET"])
def get_nodos():
    """Obtiene la lista completa de nodos con todos sus campos."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Se selecciona el campo 'fecha' de la DB
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
                # *** CAMBIO CLAVE AQUÍ: Se mapea 'fecha' (row[7]) a 'ultima_modificacion' ***
                "ultima_modificacion": row[7] 
            })
        return jsonify(nodos)
    except Exception as e:
        return jsonify({"error": f"Error al obtener nodos: {str(e)}"}), 500


# ➕ Agregar un nuevo nodo
@app.route("/nodos", methods=["POST"])
def add_nodo():
    """Agrega un nuevo nodo a la base de datos."""
    data = request.json
    nodo = data.get("nodo")
    placa = data.get("placa")
    puerto = data.get("puerto")
    
    # Inicializa la fecha al momento de la creación
    fecha_creacion = datetime.now()

    if not nodo:
        return jsonify({"error": "El campo 'nodo' es obligatorio"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO nodos (nodo, placa, puerto, fecha)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (nodo, placa, puerto, fecha_creacion))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Nodo agregado correctamente", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": f"Error al agregar nodo: {str(e)}"}), 500


# ✏️ Editar bandwidth y técnico
# *** CAMBIO CLAVE AQUÍ: Se cambió la ruta a '/nodo/<int:id>' para coincidir con el JS ***
@app.route("/nodo/<int:id>", methods=["PUT"])
def update_nodo(id):
    """Actualiza los campos de bandwidth y técnico, y la fecha de última modificación."""
    data = request.json
    up = data.get("bandwidth_up")
    down = data.get("bandwidth_down")
    tecnico = data.get("tecnico")
    
    # Guarda la hora actual de la modificación
    fecha_actualizacion = datetime.now() 

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
        """, (up, down, tecnico, fecha_actualizacion, id))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Nodo actualizado correctamente"})
    except Exception as e:
        return jsonify({"error": f"Error al actualizar nodo: {str(e)}"}), 500


# --- Ejecución ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
