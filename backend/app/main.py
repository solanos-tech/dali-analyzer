from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

import threading
import time
import webbrowser
import random

import uvicorn

app = FastAPI(title="DALI Analyzer API")


# =========================
# API ENDPOINTS
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}


def get_mock_frames() -> list[dict]:
    return [
        {"timestamp": "12:00:01", "address": "0x01", "command": "ON", "source": "mock"},
        {"timestamp": "12:00:02", "address": "0x02", "command": "OFF", "source": "mock"},
        {"timestamp": "12:00:03", "address": "0x03", "command": "DIM 50%", "source": "mock"},
    ]


def get_serial_frames() -> list[dict]:
    # placeholder - simulated "live" data
    commands = ["ON", "OFF", "DIM 25%", "DIM 50%", "DIM 75%", "QUERY"]
    addresses = ["0x01", "0x02", "0x03", "0x0A"]

    return [
        {
            "timestamp": "live",
            "address": random.choice(addresses),
            "command": random.choice(commands),
            "source": "serial",
        }
        for _ in range(3)
    ]


@app.get("/api/frames")
def get_frames(source: str = Query(default="mock")):
    if source == "serial":
        return get_serial_frames()

    return get_mock_frames()


# =========================
# UI: HOME PAGE
# =========================

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DALI Analyzer</title>
        <style>
            body {
                font-family: Arial;
                background: #f4f7fb;
                padding: 40px;
                color: #1f2937;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.08);
            }
            h1 { margin-top: 0; }
            .status {
                display: inline-block;
                padding: 8px 14px;
                border-radius: 999px;
                background: #dcfce7;
                color: #166534;
                font-weight: bold;
            }
            button {
                margin-top: 15px;
                padding: 12px 18px;
                border-radius: 10px;
                border: none;
                background: #2563eb;
                color: white;
                cursor: pointer;
            }
            button:hover {
                background: #1d4ed8;
            }
            pre {
                background: #111827;
                color: white;
                padding: 16px;
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DALI Analyzer</h1>

            <h2>Backend status</h2>
            <span class="status">Running</span>

            <br>
            <button onclick="checkHealth()">Check /health</button>
            <pre id="result">...</pre>

            <br><br>
            <a href="/frames">
                <button>Open Frames Viewer</button>
            </a>
        </div>

        <script>
            async function checkHealth() {
                const res = await fetch("/health");
                const data = await res.json();
                document.getElementById("result").textContent =
                    JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """


# =========================
# UI: FRAMES PAGE
# =========================

@app.get("/frames", response_class=HTMLResponse)
def frames_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DALI Frames</title>
        <style>
            body {
                font-family: Arial;
                background: #f4f7fb;
                padding: 40px;
                color: #1f2937;
            }
            .container {
                max-width: 1000px;
                margin: auto;
                background: white;
                padding: 24px;
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.08);
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                border-bottom: 1px solid #e5e7eb;
            }
            th {
                background: #111827;
                color: white;
            }
            button {
                padding: 10px 14px;
                border-radius: 8px;
                border: none;
                background: #2563eb;
                color: white;
                cursor: pointer;
            }
            select {
                padding: 10px;
            }
            .toolbar {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">

            <a href="/">â† Back</a>

            <h1>Frames Viewer</h1>

            <div class="toolbar">
                <select id="source">
                    <option value="mock">Mock</option>
                    <option value="serial">Serial</option>
                </select>

                <button onclick="loadFrames()">Load once</button>
                <button onclick="startLive()">Start live</button>
                <button onclick="stopLive()">Stop</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Address</th>
                        <th>Command</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody id="table"></tbody>
            </table>

        </div>

        <script>
            let timer = null;

            async function loadFrames() {
                const source = document.getElementById("source").value;
                const res = await fetch(`/api/frames?source=${source}`);
                const data = await res.json();

                const table = document.getElementById("table");
                table.innerHTML = "";

                data.forEach(f => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${f.timestamp}</td>
                        <td>${f.address}</td>
                        <td>${f.command}</td>
                        <td>${f.source}</td>
                    `;
                    table.appendChild(row);
                });
            }

            function startLive() {
                stopLive();
                loadFrames();
                timer = setInterval(loadFrames, 1000);
            }

            function stopLive() {
                if (timer) clearInterval(timer);
            }
        </script>

    </body>
    </html>
    """


# =========================
# CLI ENTRYPOINT
# =========================

def _open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000/")


def run():
    threading.Thread(target=_open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
