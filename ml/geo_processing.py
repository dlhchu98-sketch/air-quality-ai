"""
Module xử lý địa không gian bằng GeoPandas (CRS, Spatial Join, Khoảng cách UTM, Ranh giới quận).
Đáp ứng yêu cầu:
1. Đọc và kiểm tra hệ tọa độ CRS (WGS84 EPSG:4326).
2. Chuyển đổi sang hệ tọa độ phẳng mét UTM Zone 48N (EPSG:32648) để tính diện tích và khoảng cách.
3. Thực hiện Spatial Join (sjoin) giữa trạm quan trắc và đa giác quận.
4. Kiểm tra hình học hợp lệ (is_valid) và xử lý dữ liệu không gian.
"""

import sys
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
GEO_DIR = BASE_DIR / "data" / "geo"

def load_and_validate_geodata():
    """
    Nạp và kiểm chứng tính hợp lệ của dữ liệu địa không gian GeoPandas.
    """
    districts_path = GEO_DIR / "districts.geojson"
    stations_path = GEO_DIR / "stations.geojson"

    # 1. Đọc dữ liệu không gian
    gdf_districts = gpd.read_file(districts_path)
    gdf_stations = gpd.read_file(stations_path)

    # 2. Kiểm tra và chuẩn hóa CRS (Coordinate Reference System)
    if gdf_districts.crs is None:
        gdf_districts.set_crs(epsg=4326, inplace=True)
    else:
        gdf_districts = gdf_districts.to_crs(epsg=4326)

    if gdf_stations.crs is None:
        gdf_stations.set_crs(epsg=4326, inplace=True)
    else:
        gdf_stations = gdf_stations.to_crs(epsg=4326)

    # 3. Kiểm tra hình học hợp lệ
    assert gdf_districts.geometry.is_valid.all(), "Phat hien da giac quan khong hop le!"
    assert gdf_stations.geometry.is_valid.all(), "Phat hien diem tram khong hop le!"
    assert not gdf_districts.geometry.is_empty.any(), "Phat hien hinh hoc rong!"

    # 4. Chuyển đổi sang UTM Zone 48N (EPSG:32648 - Hà Nội) để tính toán độ dài và diện tích chính xác theo mét
    gdf_districts_utm = gdf_districts.to_crs(epsg=32648)
    gdf_districts["area_km2"] = (gdf_districts_utm.geometry.area / 1e6).round(2)

    # Tọa độ trung tâm Hà Nội (Hồ Hoàn Kiếm: 105.8542, 21.0285)
    center_point = gpd.GeoSeries([Point(105.8542, 21.0285)], crs="EPSG:4326").to_crs(epsg=32648).iloc[0]
    gdf_stations_utm = gdf_stations.to_crs(epsg=32648)
    gdf_stations["dist_center_km"] = (gdf_stations_utm.geometry.distance(center_point) / 1000.0).round(2)

    # 5. Phép nối không gian (Spatial Join)
    # Xác định trạm quan trắc nằm trong ranh giới quận nào thông qua quan hệ hình học 'within'
    joined = gpd.sjoin(gdf_stations, gdf_districts[["district_name", "geometry", "area_km2"]], predicate="within", how="left")

    return {
        "districts": gdf_districts,
        "stations": gdf_stations,
        "spatial_join": joined
    }

def print_geospatial_summary():
    data = load_and_validate_geodata()
    print("=== BAO CAO XU LY DIA KHONG GIAN VOI GEOPANDAS ===")
    print(f"Hệ tọa độ gốc (CRS): {data['districts'].crs}")
    print(f"Số quận/huyện xử lý: {len(data['districts'])}")
    print(f"Số trạm quan trắc: {len(data['stations'])}")
    print("\nChi tiết trạm & Khoảng cách tới trung tâm:")
    for _, row in data['stations'].iterrows():
        print(f" - [{row['station_id']}] {row['station_name']} ({row['district']}): {row['dist_center_km']} km | Loai: {row['station_type']}")
    print("\nDiện tích các quận tính bằng GeoPandas (UTM 48N):")
    for _, row in data['districts'].iterrows():
        print(f" - {row['district_name']}: {row['area_km2']} km2")
    print("==================================================")

if __name__ == "__main__":
    print_geospatial_summary()
