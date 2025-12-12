from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# In-memory storage (you can replace with MongoDB/MySQL later)
rfid_scans = []        # {uid, time}
attendance_log = []    # {usn, status, time}

# UID → USN mapping
uid_map = {
    "123456": "1RN24CS001",
    "654321": "1RN24CS002",
    "111111": "1RN24CS295"
}

@app.route("/")
def home():
    return render_template("index.html")

# ========== RFID API ===========
@app.route("/rfid", methods=["POST"])
def rfid():
    data = request.json
    uid = data.get("uid")

    rfid_scans.append({
        "uid": uid,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return jsonify({"message": "RFID recorded", "uid": uid}), 200


@app.route("/list")
def list_uids():
    return jsonify(rfid_scans)


@app.route("/map")
def get_map():
    return jsonify(uid_map)


# ========== Attendance from Facial Recognition ===========
@app.route("/api/attendance", methods=["POST"])
def attendance():
    data = request.json
    usn = data.get("usn")
    status = data.get("status")

    attendance_log.append({
        "usn": usn,
        "status": status,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return jsonify({"message": "Saved"}), 200


@app.route("/attendance_log")
def view_log():
    return jsonify(attendance_log)


# ========== Faculty Dashboard ===========
@app.route("/attendance")
def attendance_page():
    return render_template("attendance.html", data=attendance_log)


@app.route("/rfid_data")
def rfid_data():
    return render_template("rfid_data.html", data=rfid_scans)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
