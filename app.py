"""
AI WEATHER & AIR QUALITY – SMART WEATHER EXPERIENCE
Hệ thống theo dõi, so sánh & dự báo thông minh thời tiết và bụi mịn tại 34 tỉnh/thành phố Việt Nam.
Chạy file: python app.py
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
    print("\n" + "=" * 70)
    print(" 🌤️  AI WEATHER & AIR QUALITY – SMART WEATHER EXPERIENCE")
    print("     Hệ Thống Theo Dõi, Dự Báo & So Sánh 34 Tỉnh Thành Việt Nam")
    print("=" * 70)
    print(f" 🌐 1. Link Web Trực Tiếp 24/7 (Không cần máy chủ):")
    print(f"    👉 https://dlhchu98-sketch.github.io/air-quality-ai/")
    print("-" * 70)
    print(f" 💻 2. Máy Tính Cục Bộ (Localhost):")
    print(f"    👉 http://127.0.0.1:8000")
    print("-" * 70)
    print(f" 📱 3. Điện Thoại / Tablet (Chung Wi-Fi):")
    print(f"    👉 http://{wifi_ip}:8000")
    print("-" * 70)
    print(f" 📄 4. Tài Liệu API Tương Tác (Swagger UI Docs):")
    print(f"    👉 http://127.0.0.1:8000/docs")
    print("=" * 70 + "\n")
    
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)
