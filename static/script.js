// Trigger face recognition attendance
function takeAttendance() {
    fetch('/take_attendance', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert('Attendance Updated!');
            location.reload(); // Reload to show new records
        })
        .catch(error => console.error('Error:', error));
}

// Auto-refresh sensor data every 10 seconds
function refreshSensors() {
    fetch('/sensors')
        .then(response => response.json())
        .then(data => {
            document.getElementById('temperature').innerText = data.temperature + " °C";
            document.getElementById('light').innerText = data.light_level;
            if (data.light_level < 1000) {
                document.getElementById('light-status').innerText = "ON";
            } else {
                document.getElementById('light-status').innerText = "OFF";
            }
        })
        .catch(err => console.error(err));
}

// Refresh sensors immediately and then every 10s
refreshSensors();
setInterval(refreshSensors, 10000);
