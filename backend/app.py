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

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print(" Đang khởi động AirSense AI - Dự báo Chất lượng Không khí...")
    print(" Giao diện Web: http://127.0.0.1:8000")
    print(" Truy cập bằng điện thoại (cùng Wi-Fi): http://192.168.1.18:8000")
    print(" Tài liệu API: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)

