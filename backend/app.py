"""
FastAPI Main Application Entry:
- Tích hợp routers: health, spatial, air_quality, evaluation.
- Quản lý vòng đời Lifespan nạp mô hình vào RAM.
- Gắn StaticFiles phục vụ giao diện Web Frontend.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.lifespan import state
from backend.routes import health, spatial, air_quality, evaluation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động: Nạp mô hình & dữ liệu GeoPandas vào RAM
    state.startup()
    yield
    # Dọn dẹp tài nguyên khi tắt ứng dụng
    print(">>> [Lifespan] Da giai phong tai nguyen backend.")

app = FastAPI(
    title="Hệ thống AI Dự báo Chất lượng Không khí Không gian - Thời gian",
    description="Backend API phục vụ dự báo PM2.5 đa bước, tích hợp GeoPandas và tối ưu 20 CCU.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware cho phép mọi client truy cập
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router API
app.include_router(health.router)
app.include_router(spatial.router)
app.include_router(air_quality.router)
app.include_router(evaluation.router)

# Mount thư mục static phục vụ Frontend giao diện
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    if (STATIC_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=str(STATIC_DIR / "css")), name="css")
    if (STATIC_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=str(STATIC_DIR / "js")), name="js")

@app.get("/")
async def root():
    """Trang chủ chuyển hướng thẳng tới giao diện người dùng."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Air Quality Forecasting API is running. Visit /docs for Swagger UI."}

@app.get("/manifest.json")
async def manifest():
    manifest_file = STATIC_DIR / "manifest.json"
    if manifest_file.exists():
        return FileResponse(manifest_file, media_type="application/manifest+json")
    return {}

@app.get("/sw.js")
async def service_worker():
    sw_file = STATIC_DIR / "sw.js"
    if sw_file.exists():
        return FileResponse(sw_file, media_type="application/javascript")
    return {}

def get_wifi_ip():
    """Tự động phát hiện IP Wi-Fi nội bộ của máy."""
    try:
        import psutil
        addrs = psutil.net_if_addrs()
        for name, addr_list in addrs.items():
            if "wi-fi" in name.lower() or "wireless" in name.lower():
                for a in addr_list:
                    if a.family.name == "AF_INET" and not a.address.startswith("169.254"):
                        return a.address
        for name, addr_list in addrs.items():
            for a in addr_list:
                if a.family.name == "AF_INET" and (a.address.startswith("192.168.") or a.address.startswith("10.")):
                    return a.address
    except Exception:
        pass
    return "192.168.1.15"

@app.get("/api/network-info")
async def network_info():
    ip = get_wifi_ip()
    # Đường dẫn Cloud 24/7 cố định (Tắt máy chủ vẫn xem được, 3G/4G/5G vào thẳng không cần đăng nhập)
    cloud_url = "https://dlhchu98-sketch.github.io/air-quality-ai/"
    return {
        "wifi_ip": ip,
        "port": 8000,
        "direct_url": cloud_url,
        "local_url": f"http://{ip}:8000"
    }

if __name__ == "__main__":
    import uvicorn
    wifi_ip = get_wifi_ip()
    print("=" * 65)
    print(" 🚀 AirSense AI - Hệ Thống Dự Báo Chất Lượng Không Khí")
    print(f" 💻 Máy tính truy cập:       http://127.0.0.1:8000")
    print(f" 📱 Điện thoại vào trực tiếp: http://{wifi_ip}:8000")
    print(f" 📄 Tài liệu API (Docs):     http://127.0.0.1:8000/docs")
    print("=" * 65)
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)

