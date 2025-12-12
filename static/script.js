// Fetch latest sensor data every 5 seconds
async function fetchSensorData() {
    try {
        const response = await fetch('/sensors');
        const data = await response.json();
        document.getElementById('temp').textContent = data.temperature;
        document.getElementById('light').textContent = data.light_level;
        document.getElementById('sensor-time').textContent = data.timestamp;
    } catch (err) {
        console.error("Error fetching sensor data:", err);
    }
}

// Take face attendance when button clicked
document.getElementById('take-attendance').addEventListener('click', async () => {
    try {
        const response = await fetch('/take_attendance', { method: 'POST' });
        const data = await response.json();
        alert("Face Attendance Triggered: " + data.status);
        // Optionally reload dashboard to show new attendance
        location.reload();
    } catch (err) {
        console.error("Error taking attendance:", err);
    }
});

// Start fetching sensor data
setInterval(fetchSensorData, 5000);
fetchSensorData(); // initial fetch
