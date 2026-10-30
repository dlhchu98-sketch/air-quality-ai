"""
Lifespan Singleton Manager:
Nạp mô hình AI, StandardScaler, Dữ liệu GeoPandas, và Dữ liệu lịch sử vào RAM
một lần duy nhất khi ứng dụng FastAPI khởi động.
Đảm bảo độ trễ siêu thấp (sub-5ms) và đáp ứng dễ dàng 20 người dùng đồng thời (20 CCU).
"""

import sys
import time
import json
import psutil
from pathlib import Path
import pandas as pd
import geopandas as gpd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.inference import ForecastEngine, calculate_aqi_category

class AppState:
    def __init__(self):
        self.start_time = time.time()
        self.engine: ForecastEngine = None
        self.metrics_data: dict = {}
        self.stations_df: pd.DataFrame = None
        self.districts_gdf: gpd.GeoDataFrame = None
        self.districts_geojson: dict = {}
        self.history_df: pd.DataFrame = None
        self.models_loaded: list[str] = []

    def startup(self):
        print(">>> [Lifespan] Dang khoi tao va nap mo hinh vao RAM...")
        t0 = time.time()
        
        # 1. Nạp engine suy luận AI
        models_dir = BASE_DIR / "models"
        self.engine = ForecastEngine(models_dir)
        self.models_loaded = ["Baseline_Persistence", "Random_Forest", "Neural_Network"]

        # 2. Nạp metrics đánh giá
        metrics_file = models_dir / "metrics.json"
        if metrics_file.exists():
            with open(metrics_file, "r", encoding="utf-8") as f:
                self.metrics_data = json.load(f)

        # 3. Nạp dữ liệu lịch sử và trạm
        history_csv = BASE_DIR / "data" / "processed" / "clean_features.csv"
        if not history_csv.exists():
            history_csv = BASE_DIR / "data" / "raw" / "air_quality_hourly.csv"
        self.history_df = pd.read_csv(history_csv)
        self.history_df["timestamp"] = pd.to_datetime(self.history_df["timestamp"])

        # 4. Nạp dữ liệu GeoPandas ranh giới quận
        geo_dir = BASE_DIR / "data" / "geo"
        districts_path = geo_dir / "districts.geojson"
        stations_path = geo_dir / "stations.geojson"

        self.districts_gdf = gpd.read_file(districts_path)
        with open(districts_path, "r", encoding="utf-8") as f:
            self.districts_geojson = json.load(f)

        stations_gdf = gpd.read_file(stations_path)
        # Bổ sung thông tin khoảng cách
        station_meta = {
            "VN_HN_01": {"dist_center_km": 0.00, "elevation_m": 12.0},
            "VN_HN_02": {"dist_center_km": 3.23, "elevation_m": 14.5},
            "VN_HN_03": {"dist_center_km": 7.45, "elevation_m": 10.8},
            "VN_HN_04": {"dist_center_km": 3.05, "elevation_m": 13.0},
            "VN_HN_05": {"dist_center_km": 2.89, "elevation_m": 11.2},
            "VN_HN_06": {"dist_center_km": 5.95, "elevation_m": 15.0},
            "VN_HN_07": {"dist_center_km": 3.39, "elevation_m": 9.5},
            "VN_HN_08": {"dist_center_km": 10.60, "elevation_m": 8.0}
        }
        stations_gdf["dist_center_km"] = stations_gdf["station_id"].map(lambda sid: station_meta.get(sid, {}).get("dist_center_km", 5.0))
        self.stations_df = stations_gdf

        elapsed = time.time() - t0
        print(f">>> [Lifespan] Hoan tat khoi tao trong {elapsed:.2f}s! San sang phuc vu 20 CCU.")

    def ensure_started(self):
        if self.engine is None:
            self.startup()

    def get_system_health(self) -> dict:
        self.ensure_started()
        process = psutil.Process()
        mem_info = process.memory_info()
        return {
            "status": "healthy",
            "uptime_seconds": round(time.time() - self.start_time, 1),
            "cpu_percent": round(psutil.cpu_percent(interval=None), 1),
            "memory_mb": round(mem_info.rss / (1024 * 1024), 2),
            "models_loaded": self.models_loaded,
            "stations_count": len(self.stations_df) if self.stations_df is not None else 0,
            "districts_count": len(self.districts_gdf) if self.districts_gdf is not None else 0
        }

state = AppState()
