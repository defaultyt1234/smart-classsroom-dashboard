from flask import Flask, request, jsonify, render_template
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# ================= DATABASE =================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL not set")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()


# ================= TABLES =================
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    rfid_uid VARCHAR(50) UNIQUE
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method VARCHAR(10),
    status VARCHAR(10)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    temperature FLOAT,
    light INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ================= SAMPLE STUDENTS =================
students = [
    ("Shrikanth", "1RN24CS244"),
    ("Vinodkumar", "1RN24CS296")
]

for s in students:
    cur.execute("""
        INSERT INTO students (name, rfid_uid)
        VALUES (%s,%s)
        ON CONFLICT (rfid_uid) DO NOTHING
    """, s)

conn.commit()

# ================= ESP32 RFID + SENSOR =================
@app.route("/attendance", methods=["POST"])
def rfid_attendance():
    data = request.get_json()
    uid = data.get("rfid_uid", "")
    temp = data.get("temperature", None)
    light = data.get("ldr", None)
    
    # Store sensor data
    cur.execute(
        "INSERT INTO sensor_data (temperature, light) VALUES (%s,%s)",
        (temp, light)
    )
    
    # Lookup student by RFID
    cur.execute("SELECT id FROM students WHERE rfid_uid=%s", (uid,))
    s = cur.fetchone()
    if s:
        cur.execute(
            "INSERT INTO attendance (student_id, method, status) VALUES (%s,'RFID','present')",
            (s[0],)
        )

    conn.commit()
    return jsonify({"success": True})




# ================= FACE ATTENDANCE (FROM COLAB) =================
@app.route("/api/face_attendance", methods=["POST"])
def face_attendance():
    data = request.json
    usn = data["usn"]
    status = data["status"]

    cur.execute("SELECT id FROM students WHERE rfid_uid=%s", (usn,))
    s = cur.fetchone()

    if s:
        cur.execute("""
            INSERT INTO attendance (student_id, method, status)
            VALUES (%s,'FACE',%s)
        """, (s[0], status))

    conn.commit()
    return jsonify({"saved": True})

# ================= SENSOR FETCH =================
@app.route("/sensors")
def sensors():
    cur.execute("""
        SELECT temperature, light, timestamp
        FROM sensor_data ORDER BY timestamp DESC LIMIT 1
    """)
    r = cur.fetchone()

    if r:
        return jsonify({
            "temperature": r[0],
            "light": r[1],
            "time": str(r[2])
        })
    return jsonify({"temperature": "--", "light": "--"})

# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    cur.execute("""
        SELECT s.name, s.rfid_uid, a.timestamp, a.method, a.status
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        ORDER BY a.timestamp DESC
    """)
    records = cur.fetchall()
    return render_template("dashboard.html", attendance=records)

# ================= MAIN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


