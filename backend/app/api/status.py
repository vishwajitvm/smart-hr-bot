# app/api/status.py

import socket
import os
import time
import requests
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from app.core.db import client
from app.core.config import settings

router = APIRouter()

# In-memory API hits counter
API_HITS = {"health": 0, "system_health": 0}


def check_mongodb():
    start = time.time()
    try:
        client.admin.command("ping")
        return "ok", time.time() - start
    except Exception as e:
        return f"error: {str(e)}", time.time() - start


def check_logging():
    start = time.time()
    try:
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(settings.LOG_FILE, "a") as f:
            f.write("")
        return "ok", time.time() - start
    except Exception as e:
        return f"error: {str(e)}", time.time() - start


def check_env():
    start = time.time()
    required_envs = ["MONGO_URI", "MONGO_DB_NAME", "ENCRYPTION_KEY", "JWT_SECRET_KEY"]
    missing_envs = [
        var for var in required_envs
        if not getattr(settings, var, None) or getattr(settings, var) in ["", "None"]
    ]
    result = "ok" if not missing_envs else f"missing: {', '.join(missing_envs)}"
    return result, time.time() - start


def check_network():
    start = time.time()
    try:
        socket.gethostbyname("google.com")
        return "ok", time.time() - start
    except Exception as e:
        return f"error: {str(e)}", time.time() - start


def check_api(url):
    """Ping an internal API and return status + response time"""
    start = time.time()
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return "ok", time.time() - start
        else:
            return f"status {response.status_code}", time.time() - start
    except Exception as e:
        return f"error: {str(e)}", time.time() - start


@router.get("/health", response_class=JSONResponse)
def health():
    """Lightweight JSON health check."""
    API_HITS["health"] += 1

    health_status = {"app": "ok"}

    mongo_status, _ = check_mongodb()
    health_status["mongodb"] = mongo_status

    logging_status, _ = check_logging()
    health_status["logging"] = logging_status

    env_status, _ = check_env()
    health_status["env"] = env_status

    network_status, _ = check_network()
    health_status["network"] = network_status

    health_status["api_hits"] = API_HITS["health"]

    return health_status


@router.get("/system-health", response_class=HTMLResponse)
def system_health():
    """User-friendly system health dashboard."""
    API_HITS["system_health"] += 1

    checks = []

    # Core system checks
    mongodb_status, mongodb_time = check_mongodb()
    checks.append(("MongoDB", mongodb_status, mongodb_time, mongodb_status == "ok"))

    logging_status, logging_time = check_logging()
    checks.append(("Logging", logging_status, logging_time, logging_status == "ok"))

    env_status, env_time = check_env()
    checks.append(("Environment", env_status, env_time, env_status == "ok"))

    network_status, network_time = check_network()
    checks.append(("Network", network_status, network_time, network_status == "ok"))

    # Internal API checks (update URLs as per your project)
    internal_apis = [
        ("Health API", f"http://localhost:{settings.APP_PORT}/health"),
        # Add other APIs you want to monitor here
        # ("Users API", f"http://localhost:{settings.APP_PORT}/users"),
        ("Jobs API", f"http://localhost:{settings.APP_PORT}/api/jobs")
    ]
    for name, url in internal_apis:
        status, duration = check_api(url)
        checks.append((name, status, duration, status == "ok"))

    # Build HTML dashboard
    html = f"""
    <html>
        <head>
            <title>System Health Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background: #f9fafb; color: #111; }}
                h1 {{ color: #4f46e5; }}
                .check {{ margin: 10px 0; padding: 12px; border-radius: 8px; background: #fff;
                         box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex;
                         justify-content: space-between; align-items: center; transition: all 0.3s ease; }}
                .check:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }}
                .ok {{ color: green; font-weight: bold; }}
                .fail {{ color: red; font-weight: bold; }}
                .status-icon {{ font-size: 1.2rem; margin-right: 8px; }}
                .time {{ font-size: 0.9rem; color: #555; margin-left: 10px; }}
                .hits {{ margin-top: 20px; font-size: 0.95rem; color: #333; }}
            </style>
            <script>
                // Auto-refresh every 5 seconds
                setTimeout(() => {{ location.reload(); }}, 5000);
            </script>
        </head>
        <body>
            <h1>✅ System Health Dashboard</h1>
            <div>
    """

    for name, message, duration, success in checks:
        icon = "✔️" if success else "❌"
        status_class = "ok" if success else "fail"
        html += f"""
            <div class="check">
                <div><span class="status-icon">{icon}</span> <strong>{name}</strong></div>
                <div class="{status_class}">{message} <span class="time">({duration:.3f}s)</span></div>
            </div>
        """

    html += f"""
            </div>
            <div class="hits">
                API Hits: /health = {API_HITS['health']} | /system-health = {API_HITS['system_health']}
            </div>
        </body>
    </html>
    """

    return HTMLResponse(content=html)
