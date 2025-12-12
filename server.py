from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Stores scanned UIDs from ESP32
scanned = []

# Mapping UID -> USN (edit as needed)
uid_to_usn = {
    "123ABC": "1RN24CS295",
    "456DEF": "1RN24CS244"
}

# Attendance log storage
attendance_log = []


@app.route("/")
def home():
    return "Smart Attendance Server Running"


# ------------------------------
# 1) ESP32 posts UID here
# ------------------------------
@app.route("/api/nfc_event", methods=["POST"])
def nfc_event():
    data = request.json
    uid = data.get("uid")
    ts = time.time()

    scanned.append({"uid": uid, "ts": ts})
    print("Received UID:", uid)

    return jsonify({"status": "ok", "received_uid": uid})


# ------------------------------
# 2) Retrieve all scanned UIDs
# ------------------------------
@app.route("/list", methods=["GET"])
def list_scanned():
    return jsonify(scanned)


# ------------------------------
# 3) UID → USN mapping
# ------------------------------
@app.route("/map", methods=["GET"])
def map_get():
    return jsonify(uid_to_usn)


# ------------------------------
# 4) Face recognition sends attendance result
# ------------------------------
@app.route("/api/attendance", methods=["POST"])
def post_attendance():
    data = request.json
    usn = data.get("usn")
    status = data.get("status")
    ts = time.time()

    attendance_log.append({
        "usn": usn,
        "status": status,
        "timestamp": ts
    })

    print("Attendance updated:", usn, " → ", status)
    return jsonify({"status": "stored"})


# ------------------------------
# 5) Retrieve attendance log
# ------------------------------
@app.route("/attendance_log", methods=["GET"])
def get_attendance_log():
    return jsonify(attendance_log)


# ------------------------------
# RUN SERVER (Render uses Gunicorn)
# ------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
