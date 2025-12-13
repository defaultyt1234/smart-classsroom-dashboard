setInterval(() => {
    fetch("/sensors")
    .then(res => res.json())
    .then(data => {
        document.getElementById("temp").innerText = data.temperature;
        document.getElementById("light").innerText = data.light;
    });
}, 5000);
