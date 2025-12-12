from flask import Flask, request, jsonify, render_template
import psycopg2
from datetime import datetime

app = Flask(__name__)

# --- Database Connection ---
conn = psycopg2.connect(
    dbname="attendance_db",
    user="youruser",
    password="yourpassword",
    host="yourhost"
)
cur = conn.cursor()

# --- API to receive ESP32 data ---
@app.route('/attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    uid = data['uid']
    temp = data['temperature']
    light = data['light']

    cur.execute("INSERT INTO sensor_data (temperature, light_level) VALUES (%s,%s)", (temp, light))

    cur.execute("SELECT id FROM students WHERE rfid_uid=%s", (uid,))
    student = cur.fetchone()
    if student:
        student_id = student[0]
        cur.execute("INSERT INTO attendance (student_id, timestamp, method) VALUES (%s,%s,'RFID')",
                    (student_id, datetime.now()))
    conn.commit()
    return jsonify({"status": "success"}), 200

# --- Dashboard ---
@app.route('/')
def dashboard():
    cur.execute("SELECT s.name, a.timestamp, a.method FROM attendance a JOIN students s ON a.student_id = s.id ORDER BY a.timestamp DESC")
    records = cur.fetchall()
    return render_template('dashboard.html', attendance=records)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
