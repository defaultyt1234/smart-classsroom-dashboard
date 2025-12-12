function takeAttendance() {
    fetch('/take_attendance', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert('Attendance Updated!');
            location.reload(); // reload page to show new records
        })
        .catch(error => console.error('Error:', error));
}
