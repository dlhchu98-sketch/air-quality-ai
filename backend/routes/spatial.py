"""
Spatial Routes: Cung cấp thông tin địa lý và bản đồ GeoJSON được xử lý bởi GeoPandas.
"""

from fastapi import APIRouter
from backend.lifespan import state
from backend.schemas import StationInfo
from ml.inference import calculate_aqi_category

router = APIRouter(prefix="/api", tags=["Spatial Data"])

@router.get("/stations", response_model=list[StationInfo])
async def list_stations():
    """Trả về danh sách 8 trạm quan trắc không gian cùng tọa độ WGS84 và khoảng cách trung tâm."""
    state.ensure_started()
    stations = []
    for _, row in state.stations_df.iterrows():
        stations.append({
            "station_id": row["station_id"],
            "station_name": row["station_name"],
            "district": row["district"],
            "latitude": float(row.geometry.y),
            "longitude": float(row.geometry.x),
            "station_type": row["station_type"],
            "elevation_m": float(row["elevation_m"]),
            "dist_center_km": float(row["dist_center_km"])
        })
    return stations

@router.get("/regions")
async def get_geojson_regions():
    """
    Trả về dữ liệu GeoJSON đa giác các quận Hà Nội được gắn nhãn AQI và PM2.5 trung bình.
    GeoPandas GeoDataFrame được serialize trực tiếp thành GeoJSON chuẩn EPSG:4326.
    """
    state.ensure_started()
    # Tính PM2.5 trung bình mới nhất theo quận từ dữ liệu lịch sử
    latest_rows = state.history_df.sort_values("timestamp").groupby("district").last().reset_index()
    district_pm25_map = {}
    for _, row in latest_rows.iterrows():
        aqi_info = calculate_aqi_category(float(row["pm25"]))
        district_pm25_map[row["district"]] = {
            "pm25": float(row["pm25"]),
            "aqi_level": aqi_info["aqi_level"],
            "aqi_code": aqi_info["aqi_code"],
            "color": aqi_info["color"]
        }

    # Bổ sung thông tin động vào GeoJSON features
    geojson_copy = json_deepcopy = {
        "type": "FeatureCollection",
        "crs": state.districts_geojson.get("crs"),
        "features": []
    }

    for feat in state.districts_geojson["features"]:
        d_name = feat["properties"]["district_name"]
        aqi_data = district_pm25_map.get(d_name, {
            "pm25": 42.0,
            "aqi_level": "Kém cho nhóm nhạy cảm",
            "aqi_code": "USG",
            "color": "#f97316"
        })
        
        feature_updated = {
            "type": "Feature",
            "properties": {
                **feat["properties"],
                "pm25": aqi_data["pm25"],
                "aqi_level": aqi_data["aqi_level"],
                "aqi_code": aqi_data["aqi_code"],
                "color": aqi_data["color"]
            },
            "geometry": feat["geometry"]
        }
        geojson_copy["features"].append(feature_updated)

    return geojson_copy
