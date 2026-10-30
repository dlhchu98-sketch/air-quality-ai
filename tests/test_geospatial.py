"""
Unit test kiểm thử dữ liệu địa không gian với GeoPandas.
"""

import sys
from pathlib import Path
import pytest
import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.geo_processing import load_and_validate_geodata

def test_geodata_crs_and_validity():
    data = load_and_validate_geodata()
    gdf_districts = data["districts"]
    gdf_stations = data["stations"]

    # 1. Kiểm tra hệ tọa độ CRS WGS84
    assert str(gdf_districts.crs) == "EPSG:4326", f"CRS quan phai la EPSG:4326, nhan duoc: {gdf_districts.crs}"
    assert str(gdf_stations.crs) == "EPSG:4326", f"CRS tram phai la EPSG:4326, nhan duoc: {gdf_stations.crs}"

    # 2. Kiểm tra tính hợp lệ của geometry
    assert gdf_districts.geometry.is_valid.all(), "Ton tai da giac khong hop le!"
    assert gdf_stations.geometry.is_valid.all(), "Ton tai diem tram khong hop le!"
    assert len(gdf_districts) == 8, "So luong quan phai bang 8"
    assert len(gdf_stations) == 8, "So luong tram phai bang 8"

    # 3. Kiểm tra tính toán diện tích và khoảng cách
    assert (gdf_districts["area_km2"] > 0).all(), "Dien tich cac quan phai > 0"
    assert (gdf_stations["dist_center_km"] >= 0).all(), "Khoang cach phai >= 0"

def test_spatial_join():
    data = load_and_validate_geodata()
    joined = data["spatial_join"]
    
    assert len(joined) == 8, "Spatial join phai giu du 8 tram quan trac"
    assert not joined["district_name"].isnull().any(), "Tat ca cac tram phai nam trong mot quan xac dinh"
