"""
AirSense AI - Hệ Thống Dự Báo Chất Lượng Không Khí Đô Thị
Chạy lệnh: python main.py
"""

import sys
from pathlib import Path
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app import app, get_wifi_ip

if __name__ == "__main__":
    wifi_ip = get_wifi_ip()
    print("=" * 65)
    print(" 🚀 AirSense AI - Dự Báo Chất Lượng Không Khí Đang Chạy!")
    print(f" 💻 Máy tính truy cập:        http://127.0.0.1:8000")
    print(f" 📱 Quét vào trực tiếp (ĐT):  http://{wifi_ip}:8000")
    print(f" 📄 Tài liệu API (Docs):      http://127.0.0.1:8000/docs")
    print("=" * 65)
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
