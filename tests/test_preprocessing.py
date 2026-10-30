"""
Unit test kiểm thử pipeline tiền xử lý và đặc trưng chuỗi thời gian.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.data_processing import clean_and_impute, create_features, split_chronological, FEATURE_COLS, TARGET_COL

def test_clean_and_impute():
    # Tạo sample df có missing value và duplicate
    raw_data = {
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 00:00:00", "2024-01-01 01:00:00", "2024-01-01 02:00:00"],
        "station_id": ["VN_HN_01", "VN_HN_01", "VN_HN_01", "VN_HN_01"],
        "pm25": [30.0, 30.0, np.nan, 35.0],
        "pm10": [50.0, 50.0, 55.0, np.nan],
        "temperature": [20.0, 20.0, 21.0, 22.0],
        "humidity": [70.0, 70.0, 68.0, 65.0],
        "wind_speed": [2.0, 2.0, 2.5, 3.0]
    }
    df = pd.DataFrame(raw_data)
    cleaned = clean_and_impute(df)

    assert len(cleaned) == 3, "Phải loại bỏ đúng dòng trùng lặp"
    assert not cleaned["pm25"].isnull().any(), "Không được còn giá trị null trong cột PM2.5"
    assert not cleaned["pm10"].isnull().any(), "Không được còn giá trị null trong cột PM10"

def test_create_features():
    # Nạp dữ liệu thực tế
    raw_csv = BASE_DIR / "data" / "raw" / "air_quality_hourly.csv"
    if not raw_csv.exists():
        pytest.skip("Chưa có raw data csv")
    
    df = pd.read_csv(raw_csv).head(500)
    cleaned = clean_and_impute(df)
    features_df = create_features(cleaned)

    # Kiểm tra các cột đặc trưng bắt buộc
    for col in FEATURE_COLS:
        assert col in features_df.columns, f"Thiếu cột đặc trưng {col}"
    assert TARGET_COL in features_df.columns, "Thiếu cột target"
    assert not features_df[FEATURE_COLS].isnull().any().any(), "Không được chứa NaN trong ma trận đặc trưng"

def test_chronological_split():
    # Kiểm tra phân chia không bị rò rỉ dữ liệu (No Data Leakage)
    timestamps = pd.date_range("2024-01-01", periods=100, freq="h")
    df = pd.DataFrame({
        "timestamp": timestamps,
        "val": range(100)
    })
    train_df, val_df, test_df = split_chronological(df, 0.7, 0.15)
    
    assert train_df["timestamp"].max() < val_df["timestamp"].min(), "Rò rỉ giữa train và val!"
    assert val_df["timestamp"].max() < test_df["timestamp"].min(), "Rò rỉ giữa val và test!"
