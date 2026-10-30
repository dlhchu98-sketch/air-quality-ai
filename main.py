"""
Main entry point for AirSense AI.
Chạy ứng dụng: python main.py
"""

import sys
from pathlib import Path
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app import app

if __name__ == "__main__":
    print("=" * 60)
    print(" Đang khởi động AirSense AI - Dự báo Chất lượng Không khí...")
    print(" Giao diện Web: http://127.0.0.1:8000")
    print(" Tài liệu API: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
