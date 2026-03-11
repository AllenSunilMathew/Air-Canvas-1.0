import subprocess
import webbrowser
import time
import os

# === PATHS ===
PROJECT_DIR = r"D:\A project -Inker\Sketch-To-Image\Sketch-To-Image"
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")

# venv is outside backend
VENV_PYTHON = os.path.join(PROJECT_DIR, "venv", "Scripts", "python.exe")

HTML_AIR = os.path.join(PROJECT_DIR, "frontend", "air.html")
HTML_DRAW = os.path.join(PROJECT_DIR, "frontend", "draw.html")
HTML_RES = os.path.join(PROJECT_DIR, "frontend", "result.html")

# === Start FastAPI backend ===
subprocess.Popen(
    [VENV_PYTHON, "-m", "uvicorn", "main:app", "--reload"],
    cwd=BACKEND_DIR
)

# Wait for server to start
time.sleep(3)

# === Open frontend - air.html (camera/sketch), draw.html and result.html ===
webbrowser.open(f"file:///{HTML_AIR}")
time.sleep(1)
webbrowser.open(f"file:///{HTML_DRAW}")
time.sleep(1)
webbrowser.open(f"file:///{HTML_RES}")

print("✅ Backend started and frontend opened")
