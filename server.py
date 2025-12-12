from flask import Flask, request, jsonify, render_template
import psycopg2
from datetime import datetime

app = Flask(__name__)

# ------------------ Database Connection ------------------
conn = psycopg2.connect(
    dbname="attendance_db",   # your DB name
    user="youruser",          # your DB user
    password="yourpassword",  # your DB password
    host="yourhost"           # your DB host (from Render)
)
cur = conn.cursor()

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
    cur.execute("""
        SELECT s.name, a.timestamp, a.method
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.timestamp DESC
    """)
    records = cur.fetchall()
    return render_template('dashboard.html', attendance=records)

# ------------------ Face Attendance Endpoint ------------------
@app.route('/take_attendance', methods=['POST'])
def take_face_attendance():
    # Placeholder: Trigger your DeepFace code here
    # Example: Run facial recognition and insert attendance
    return jsonify({"status": "success"})

# ------------------ Main ------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
