"""
Script tạo dữ liệu địa lý GeoJSON chuẩn (EPSG:4326) và dữ liệu chuỗi thời gian chất lượng không khí.
Dữ liệu đại diện cho mạng lưới 8 trạm quan trắc tại Hà Nội với quy luật vật lý:
- Chu kỳ ngày/đêm (diurnal cycle: cao điểm giao thông 7-9h và 17-20h)
- Nghịch nhiệt mùa đông / biến thiên theo mùa (mùa hanh khô ô nhiễm cao hơn)
- Tương quan giữa bụi mịn PM2.5/PM10 và khí thải NO2, CO
- Giá trị thiếu tự nhiên (missing values) để kiểm chứng pipeline làm sạch dữ liệu
"""

import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
GEO_DIR = BASE_DIR / "data" / "geo"
RAW_DIR = BASE_DIR / "data" / "raw"
GEO_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

# 1. Danh sách trạm quan trắc thực tế với tọa độ WGS84 (EPSG:4326)
STATIONS = [
    {
        "station_id": "VN_HN_01",
        "station_name": "Trạm Hoàn Kiếm (Đinh Tiên Hoàng)",
        "district": "Hoàn Kiếm",
        "latitude": 21.0285,
        "longitude": 105.8542,
        "station_type": "Giao thông đô thị",
        "elevation_m": 12.0
    },
    {
        "station_id": "VN_HN_02",
        "station_name": "Trạm Ba Đình (Kim Mã)",
        "district": "Ba Đình",
        "latitude": 21.0333,
        "longitude": 105.8235,
        "station_type": "Khu dân cư hỗn hợp",
        "elevation_m": 14.5
    },
    {
        "station_id": "VN_HN_03",
        "station_name": "Trạm Cầu Giấy (Xuân Thủy)",
        "district": "Cầu Giấy",
        "latitude": 21.0368,
        "longitude": 105.7831,
        "station_type": "Giao thông cửa ngõ",
        "elevation_m": 10.8
    },
    {
        "station_id": "VN_HN_04",
        "station_name": "Trạm Đống Đa (Nguyễn Lương Bằng)",
        "district": "Đống Đa",
        "latitude": 21.0189,
        "longitude": 105.8267,
        "station_type": "Khu dân cư mật độ cao",
        "elevation_m": 13.0
    },
    {
        "station_id": "VN_HN_05",
        "station_name": "Trạm Hai Bà Trưng (Minh Khai)",
        "district": "Hai Bà Trưng",
        "latitude": 21.0025,
        "longitude": 105.8569,
        "station_type": "Giao thông & dân cư",
        "elevation_m": 11.2
    },
    {
        "station_id": "VN_HN_06",
        "station_name": "Trạm Tây Hồ (Lạc Long Quân)",
        "district": "Tây Hồ",
        "latitude": 21.0652,
        "longitude": 105.8123,
        "station_type": "Đô thị sinh thái hồ",
        "elevation_m": 15.0
    },
    {
        "station_id": "VN_HN_07",
        "station_name": "Trạm Long Biên (Nguyễn Văn Cừ)",
        "district": "Long Biên",
        "latitude": 21.0489,
        "longitude": 105.8785,
        "station_type": "Khu cửa ngõ phía Đông",
        "elevation_m": 9.5
    },
    {
        "station_id": "VN_HN_08",
        "station_name": "Trạm Hà Đông (Quang Trung)",
        "district": "Hà Đông",
        "latitude": 20.9712,
        "longitude": 105.7725,
        "station_type": "Khu đô thị vệ tinh",
        "elevation_m": 8.0
    }
]

# 2. Tạo ranh giới đa giác các quận (Districts GeoJSON)
DISTRICT_POLYGONS = {
    "Hoàn Kiếm": [
        [105.845, 21.022], [105.862, 21.020], [105.865, 21.036],
        [105.850, 21.040], [105.842, 21.031], [105.845, 21.022]
    ],
    "Ba Đình": [
        [105.810, 21.025], [105.842, 21.025], [105.845, 21.045],
        [105.825, 21.050], [105.808, 21.038], [105.810, 21.025]
    ],
    "Cầu Giấy": [
        [105.770, 21.020], [105.805, 21.020], [105.810, 21.048],
        [105.778, 21.052], [105.765, 21.035], [105.770, 21.020]
    ],
    "Đống Đa": [
        [105.812, 21.005], [105.838, 21.008], [105.842, 21.025],
        [105.815, 21.028], [105.808, 21.018], [105.812, 21.005]
    ],
    "Hai Bà Trưng": [
        [105.838, 20.990], [105.870, 20.995], [105.872, 21.020],
        [105.842, 21.020], [105.838, 20.990]
    ],
    "Tây Hồ": [
        [105.800, 21.045], [105.845, 21.045], [105.850, 21.085],
        [105.810, 21.090], [105.795, 21.065], [105.800, 21.045]
    ],
    "Long Biên": [
        [105.865, 21.025], [105.910, 21.030], [105.920, 21.075],
        [105.870, 21.080], [105.860, 21.050], [105.865, 21.025]
    ],
    "Hà Đông": [
        [105.750, 20.950], [105.795, 20.955], [105.800, 20.985],
        [105.760, 20.990], [105.745, 20.970], [105.750, 20.950]
    ]
}

def export_geojson_files():
    # Export stations
    station_features = []
    for s in STATIONS:
        feature = {
            "type": "Feature",
            "properties": {
                "station_id": s["station_id"],
                "station_name": s["station_name"],
                "district": s["district"],
                "station_type": s["station_type"],
                "elevation_m": s["elevation_m"]
            },
            "geometry": {
                "type": "Point",
                "coordinates": [s["longitude"], s["latitude"]]
            }
        }
        station_features.append(feature)
        
    stations_geojson = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": station_features
    }
    with open(GEO_DIR / "stations.geojson", "w", encoding="utf-8") as f:
        json.dump(stations_geojson, f, ensure_ascii=False, indent=2)

    # Export districts
    district_features = []
    for district_name, coords in DISTRICT_POLYGONS.items():
        feature = {
            "type": "Feature",
            "properties": {
                "district_name": district_name,
                "city": "Hà Nội",
                "country": "Vietnam"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }
        district_features.append(feature)
        
    districts_geojson = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": district_features
    }
    with open(GEO_DIR / "districts.geojson", "w", encoding="utf-8") as f:
        json.dump(districts_geojson, f, ensure_ascii=False, indent=2)
    print("[OK] Da luu data/geo/stations.geojson va data/geo/districts.geojson")

def generate_hourly_data(days=180, seed=42):
    """
    Sinh chuỗi dữ liệu 180 ngày (4,320 giờ/trạm x 8 trạm = 34,560 dòng)
    với quy luật vật lý chuẩn:
    - Diurnal cycle: cao điểm 7-9h sáng và 17-20h tối
    - Mùa vụ (mùa đông ô nhiễm cao hơn)
    - Tương quan nghịch với tốc độ gió (gió to làm phân tán bụi)
    - Tương quan thuận giữa PM2.5 và PM10 (~ 0.65)
    """
    np.random.seed(seed)
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    timestamps = [start_time + timedelta(hours=i) for i in range(days * 24)]
    
    rows = []
    
    # Hệ số nền theo trạm (trạm giao thông ô nhiễm hơn trạm sinh thái)
    station_traffic_bias = {
        "VN_HN_01": 1.15, # Hoàn Kiếm trung tâm
        "VN_HN_02": 1.05, # Ba Đình
        "VN_HN_03": 1.25, # Cầu Giấy cửa ngõ giao thông lớn
        "VN_HN_04": 1.10, # Đống Đa
        "VN_HN_05": 1.20, # Minh Khai - Hai Bà Trưng
        "VN_HN_06": 0.85, # Tây Hồ gần hồ thoáng khí
        "VN_HN_07": 1.00, # Long Biên
        "VN_HN_08": 1.12  # Hà Đông
    }

    for dt in timestamps:
        hour = dt.hour
        month = dt.month
        day_of_week = dt.weekday()
        
        # Mùa: tháng 1-3 (mùa đông hanh khô ô nhiễm cao), tháng 5-6 (hè mưa phân tán tốt hơn)
        season_factor = 1.35 if month in [1, 2, 12] else (1.1 if month in [3, 11] else 0.85)
        
        # Diurnal pattern: giờ cao điểm sáng và chiều tối
        rush_hour_morning = np.exp(-((hour - 8) ** 2) / 4) * 25.0
        rush_hour_evening = np.exp(-((hour - 18.5) ** 2) / 6) * 30.0
        night_inversion = 12.0 if (hour <= 5 or hour >= 22) else 0.0
        base_pm25 = 28.0 + rush_hour_morning + rush_hour_evening + night_inversion
        
        # Khí tượng
        temp = 20.0 + 7.0 * np.sin(np.pi * (hour - 9) / 12) + (month - 6) * 1.5 + np.random.normal(0, 1.2)
        humidity = 75.0 - 15.0 * np.sin(np.pi * (hour - 9) / 12) + np.random.normal(0, 3.5)
        humidity = np.clip(humidity, 35.0, 98.0)
        wind_speed = np.abs(2.2 + 1.5 * np.sin(np.pi * (hour - 11) / 12) + np.random.normal(0, 0.6))
        
        # Gió càng mạnh phân tán ô nhiễm càng tốt
        dispersion = np.clip(3.0 / (wind_speed + 0.5), 0.5, 2.2)

        for s in STATIONS:
            s_id = s["station_id"]
            bias = station_traffic_bias[s_id]
            
            # Nhiễu ngẫu nhiên trạm
            noise = np.random.normal(0, 4.0)
            
            pm25 = (base_pm25 * season_factor * dispersion * bias) + noise
            pm25 = float(np.clip(pm25, 5.0, 280.0))
            
            # PM10 tỉ lệ thuận với PM2.5 (PM2.5 thường chiếm 55-75% PM10 ở đô thị)
            pm10 = pm25 / np.random.uniform(0.55, 0.70) + np.random.normal(0, 3.0)
            pm10 = float(np.clip(pm10, pm25 + 2.0, 350.0))
            
            # NO2 phát sinh từ đốt nhiên liệu giao thông
            no2 = (18.0 + (rush_hour_morning + rush_hour_evening) * 0.9) * bias * dispersion + np.random.normal(0, 2.5)
            no2 = float(np.clip(no2, 5.0, 140.0))
            
            # CO (mg/m³)
            co = (0.6 + (rush_hour_morning + rush_hour_evening) * 0.04) * bias * dispersion + np.random.normal(0, 0.08)
            co = float(np.clip(co, 0.2, 5.5))
            
            # O3 thường cao vào buổi trưa nhiều nắng (phản ứng quang hóa)
            solar_o3 = np.maximum(0, np.sin(np.pi * (hour - 6) / 12)) * 55.0
            o3 = (15.0 + solar_o3) / (bias * 0.8) + np.random.normal(0, 3.0)
            o3 = float(np.clip(o3, 5.0, 160.0))
            
            # SO2
            so2 = (8.0 + np.random.normal(0, 1.5)) * dispersion
            so2 = float(np.clip(so2, 2.0, 60.0))
            
            rows.append({
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "station_id": s_id,
                "station_name": s["station_name"],
                "district": s["district"],
                "latitude": s["latitude"],
                "longitude": s["longitude"],
                "pm25": round(pm25, 2),
                "pm10": round(pm10, 2),
                "no2": round(no2, 2),
                "co": round(co, 3),
                "o3": round(o3, 2),
                "so2": round(so2, 2),
                "temperature": round(temp, 1),
                "humidity": round(humidity, 1),
                "wind_speed": round(wind_speed, 2)
            })

    df = pd.DataFrame(rows)
    
    # Bổ sung 1.2% giá trị thiếu ngẫu nhiên (để pipeline tiền xử lý thể hiện năng lực làm sạch)
    np.random.seed(seed)
    mask_missing = np.random.rand(len(df)) < 0.012
    df.loc[mask_missing, "pm25"] = np.nan
    mask_missing_no2 = np.random.rand(len(df)) < 0.008
    df.loc[mask_missing_no2, "no2"] = np.nan

    out_csv = RAW_DIR / "air_quality_hourly.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[OK] Da sinh du lieu quan trac: {len(df)} dong tai {out_csv}")
    print(f"  Khoang thoi gian: tu {timestamps[0]} den {timestamps[-1]}")
    print(f"  So tram: {len(STATIONS)} tram quan trac khong gian")

if __name__ == "__main__":
    export_geojson_files()
    generate_hourly_data(days=180)
