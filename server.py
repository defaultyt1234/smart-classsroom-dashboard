from flask import Flask, request, jsonify, render_template
import psycopg2
from datetime import datetime
import cv2
from deepface import DeepFace
import os
from datetime import datetime

def run_face_attendance(cur, conn):
    db_path = "static/students"
    cap = cv2.VideoCapture(0)  # use default webcam

    detected_usns = set()
    SCAN_FRAMES = 10

    for _ in range(SCAN_FRAMES):
        ret, frame = cap.read()
        if not ret:
            continue

        try:
            result = DeepFace.find(img_path=frame, db_path=db_path, enforce_detection=False, distance_metric="cosine")
            if len(result) > 0 and not result[0].empty:
                matched_file = result[0].iloc[0]['identity']
                usn = os.path.basename(matched_file).split('.')[0]
                detected_usns.add(usn)
        except:
            pass

    cap.release()

    # Insert detected attendance into DB
    for usn in detected_usns:
        cur.execute(
            "INSERT INTO attendance (student_id, timestamp, method) "
            "SELECT id, %s, 'Face' FROM students WHERE rfid_uid=%s",
            (datetime.now(), usn)
        )
    conn.commit()
    return list(detected_usns)



app = Flask(__name__)

# ------------------ Database Connection ------------------
conn = psycopg2.connect(
    dbname="attendance_db",  
    user="attendance_db_cfay_user",          
    password="ZHJLQyejo3kni7HdezxvakMi881BrKFq",  
    host="dpg-d4u6niqdbo4c7389oqe0-a.render.com",  
    port=5432
)
cur = conn.cursor()

# ------------------ Create Tables (run once at startup) ------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    rfid_uid VARCHAR(50) UNIQUE,
    face_encoding TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method VARCHAR(10)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    temperature FLOAT,
    light_level INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# ------------------ Insert Sample Students (Optional) ------------------
sample_students = [
    ("Shrikanth ", "1RN24CS244"),
    ("Vinodkumar", "1RN24CS296")
]

for name, rfid in sample_students:
    cur.execute("""
        INSERT INTO students (name, rfid_uid) 
        VALUES (%s, %s) 
        ON CONFLICT (rfid_uid) DO NOTHING
    """, (name, rfid))

conn.commit()

# ------------------ API to Receive ESP32 Data ------------------
@app.route('/attendance', methods=['POST'])
def mark_rfid_attendance():
    try:
        data = request.get_json()
        uid = data['uid']
        temp = data['temperature']
        light = data['light']

        # Store sensor data
        cur.execute(
            "INSERT INTO sensor_data (temperature, light_level) VALUES (%s,%s)",
            (temp, light)
        )

        # Lookup student by RFID UID
        cur.execute("SELECT id FROM students WHERE rfid_uid=%s", (uid,))
        student = cur.fetchone()
        if student:
            student_id = student[0]
            cur.execute(
                "INSERT INTO attendance (student_id, timestamp, method) VALUES (%s,%s,'RFID')",
                (student_id, datetime.now())
            )

        conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------ API to Return Latest Sensor Data ------------------
@app.route('/sensors', methods=['GET'])
def get_sensor_data():
    try:
        cur.execute(
            "SELECT temperature, light_level, timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 1"
        )
        data = cur.fetchone()
        if data:
            return jsonify({
                "temperature": data[0],
                "light_level": data[1],
                "timestamp": str(data[2])
            })
        else:
            return jsonify({"temperature": "--", "light_level": "--", "timestamp": "--"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------ Dashboard ------------------
@app.route('/')
def dashboard():
    # Fetch all attendance records
    cur.execute("""
        SELECT a.id, s.name, s.rfid_uid, a.timestamp, a.method 
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.timestamp DESC
    """)
    records = cur.fetchall()
    return render_template('dashboard.html', attendance=records)

# ------------------ Face Attendance Endpoint ------------------
@app.route('/take_attendance', methods=['POST'])
def take_face_attendance():
    detected = run_face_attendance(cur, conn)
    return jsonify({"status": "success", "detected": detected})



# ------------------ Main ------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

