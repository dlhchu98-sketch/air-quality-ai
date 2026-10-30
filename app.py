"""
AirSense AI - Hệ Thống Dự Báo Chất Lượng Không Khí Đô Thị
File khởi chạy chính của dự án.
Chạy lệnh: python app.py
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
    print(" Giao diện Web máy tính: http://127.0.0.1:8000")
    print(" Truy cập bằng điện thoại (cùng Wi-Fi): http://192.168.1.18:8000")
    print(" Tài liệu API: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
