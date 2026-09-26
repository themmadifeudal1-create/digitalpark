import uvicorn
import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 60)
    print("Starting ParkIQ - Smart Campus Parking Platform")
    print("URL: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("Architecture: S.M.A.R.T. (Sensing, ML, Assured, Realtime, Timetable)")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
