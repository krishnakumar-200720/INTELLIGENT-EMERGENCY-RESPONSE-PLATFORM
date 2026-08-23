from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DATABASE_FOLDER = "database"
DATABASE = os.path.join(DATABASE_FOLDER, "emergency.db")

# --------------------------------------------------
# Create Database
# --------------------------------------------------

def create_database():
    if not os.path.exists(DATABASE_FOLDER):
        os.makedirs(DATABASE_FOLDER)

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            emergency_type TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# Intelligent Priority Calculation
# --------------------------------------------------

def calculate_priority(emergency_type, description):
    emergency_type = emergency_type.lower()
    description = description.lower()

    critical_keywords = [
        "heart",
        "cardiac",
        "unconscious",
        "accident",
        "fire",
        "critical",
        "bleeding",
        "stroke",
        "trapped"
    ]

    high_keywords = [
        "injury",
        "breathing",
        "danger",
        "violence",
        "medical",
        "emergency"
    ]

    if emergency_type in ["Fire", "Medical", "Accident"]:
        for word in critical_keywords:
            if word in description:
                return "CRITICAL"

    for word in critical_keywords:
        if word in description:
            return "CRITICAL"

    for word in high_keywords:
        if word in description:
            return "HIGH"

    if emergency_type in ["Medical", "Fire", "Accident"]:
        return "HIGH"

    return "MEDIUM"


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# Create Emergency
# --------------------------------------------------

@app.route("/api/emergency", methods=["POST"])
def create_emergency():

    data = request.get_json()

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    emergency_type = data.get("emergency_type", "").strip()
    location = data.get("location", "").strip()
    description = data.get("description", "").strip()

    if not name or not phone or not emergency_type or not location:
        return jsonify({
            "success": False,
            "message": "Please fill all required fields."
        }), 400

    priority = calculate_priority(
        emergency_type,
        description
    )

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO emergencies
        (
            name,
            phone,
            emergency_type,
            location,
            description,
            priority,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        emergency_type,
        location,
        description,
        priority,
        "Pending",
        created_at
    ))

    connection.commit()

    emergency_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "success": True,
        "message": "Emergency alert received successfully.",
        "emergency_id": emergency_id,
        "priority": priority
    })


# --------------------------------------------------
# Get All Emergencies
# --------------------------------------------------

@app.route("/api/emergencies", methods=["GET"])
def get_emergencies():

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM emergencies
        ORDER BY id DESC
    """)

    emergencies = cursor.fetchall()

    connection.close()

    result = []

    for emergency in emergencies:
        result.append(dict(emergency))

    return jsonify(result)


# --------------------------------------------------
# Update Emergency Status
# --------------------------------------------------

@app.route("/api/emergency/<int:emergency_id>", methods=["PUT"])
def update_emergency(emergency_id):

    data = request.get_json()

    status = data.get("status")

    allowed_status = [
        "Pending",
        "Dispatched",
        "In Progress",
        "Resolved"
    ]

    if status not in allowed_status:
        return jsonify({
            "success": False,
            "message": "Invalid status."
        }), 400

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE emergencies
        SET status = ?
        WHERE id = ?
    """, (status, emergency_id))

    connection.commit()

    connection.close()

    return jsonify({
        "success": True,
        "message": "Emergency status updated."
    })


# --------------------------------------------------
# Dashboard Statistics
# --------------------------------------------------

@app.route("/api/statistics", methods=["GET"])
def statistics():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM emergencies"
    )
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM emergencies WHERE status = 'Pending'"
    )
    pending = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM emergencies WHERE status = 'Dispatched'"
    )
    dispatched = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM emergencies WHERE priority = 'CRITICAL'"
    )
    critical = cursor.fetchone()[0]

    connection.close()

    return jsonify({
        "total": total,
        "pending": pending,
        "dispatched": dispatched,
        "critical": critical
    })


# --------------------------------------------------
# Run Application
# --------------------------------------------------

if __name__ == "__main__":
    create_database()

    print("-----------------------------------------")
    print(" Intelligent Emergency Response Platform")
    print("-----------------------------------------")
    print("Server running at:")
    print("http://127.0.0.1:5000")
    print("-----------------------------------------")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
