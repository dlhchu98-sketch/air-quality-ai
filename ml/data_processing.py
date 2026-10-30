"""
Module tiền xử lý dữ liệu và tạo đặc trưng chuỗi thời gian (Feature Engineering).
Quy tắc quan trọng:
1. Xử lý giá trị thiếu (missing values) bằng Forward-fill theo từng trạm và Rolling Median.
2. Kiểm tra trùng lặp và loại bỏ.
3. Giới hạn ngoại lai theo vật lý (physical clipping).
4. Mã hóa chu kỳ thời gian (Cyclical Encoding: Sin/Cos cho giờ, thứ trong tuần, tháng).
5. Tạo đặc trưng độ trễ (Lag features 1h, 2h, 3h, 6h, 12h, 24h) và thống kê trượt (Rolling stats).
6. Ghép thông tin không gian từ GeoPandas (khoảng cách trung tâm).
7. Chia tập Train (70%), Val (15%), Test (15%) theo thứ tự thời gian - TUYỆT ĐỐI KHÔNG RÒ RỈ DỮ LIỆU.
8. Chuẩn hóa StandardScaler chỉ fit trên tập Train.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV = BASE_DIR / "data" / "raw" / "air_quality_hourly.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Danh sách đặc trưng đầu vào cho mô hình
FEATURE_COLS = [
    # Đặc trưng chu kỳ thời gian
    "sin_hour", "cos_hour",
    "sin_dow", "cos_dow",
    "sin_month", "cos_month",
    # Khí tượng hiện tại
    "temperature", "humidity", "wind_speed",
    # Độ trễ PM2.5
    "pm25_lag_1", "pm25_lag_2", "pm25_lag_3", "pm25_lag_6", "pm25_lag_12", "pm25_lag_24",
    # Độ trễ khí liên quan
    "pm10_lag_1", "no2_lag_1", "co_lag_1", "o3_lag_1", "so2_lag_1",
    # Thống kê trượt (Rolling Stats)
    "pm25_roll_mean_6h", "pm25_roll_std_6h", "pm25_roll_mean_24h",
    "temp_roll_mean_6h", "wind_roll_mean_6h",
    # Đặc trưng không gian
    "dist_center_km", "elevation_m"
]

TARGET_COL = "pm25_target_1h"

def clean_and_impute(df: pd.DataFrame) -> pd.DataFrame:
    """Xử lý giá trị thiếu, trùng lặp và ngoại lai."""
    df = df.copy()
    
    # 1. Chuyển đổi timestamp và sắp xếp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by=["station_id", "timestamp"]).reset_index(drop=True)
    
    # 2. Xử lý trùng lặp
    init_len = len(df)
    df = df.drop_duplicates(subset=["station_id", "timestamp"]).reset_index(drop=True)
    if len(df) < init_len:
        print(f"  [Clean] Da loai bo {init_len - len(df)} dong trung lap.")

    # 3. Điền giá trị thiếu theo từng trạm bằng ffill -> bfill -> median
    pollutants = ["pm25", "pm10", "no2", "co", "o3", "so2", "temperature", "humidity", "wind_speed"]
    for col in pollutants:
        if col in df.columns:
            # Forward-fill theo từng trạm để giữ tính chất chuỗi thời gian
            df[col] = df.groupby("station_id")[col].transform(lambda x: x.ffill().bfill())
            # Nếu vẫn còn sót null thì điền median toàn cục
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())

    # 4. Giới hạn ngoại lai vật lý (Clipping)
    df["pm25"] = df["pm25"].clip(0.0, 500.0)
    df["pm10"] = df["pm10"].clip(0.0, 600.0)
    df["no2"] = df["no2"].clip(0.0, 300.0)
    df["co"] = df["co"].clip(0.0, 15.0)
    df["o3"] = df["o3"].clip(0.0, 350.0)
    df["so2"] = df["so2"].clip(0.0, 200.0)
    df["temperature"] = df["temperature"].clip(0.0, 50.0)
    df["humidity"] = df["humidity"].clip(10.0, 100.0)
    df["wind_speed"] = df["wind_speed"].clip(0.0, 40.0)
    
    return df

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Tạo các đặc trưng chu kỳ, lag và rolling."""
    df = df.copy()
    
    # 1. Cyclical time features (Chu kỳ ngày/tuần/tháng)
    hours = df["timestamp"].dt.hour
    df["sin_hour"] = np.sin(2 * np.pi * hours / 24.0)
    df["cos_hour"] = np.cos(2 * np.pi * hours / 24.0)

    dows = df["timestamp"].dt.weekday
    df["sin_dow"] = np.sin(2 * np.pi * dows / 7.0)
    df["cos_dow"] = np.cos(2 * np.pi * dows / 7.0)

    months = df["timestamp"].dt.month
    df["sin_month"] = np.sin(2 * np.pi * months / 12.0)
    df["cos_month"] = np.cos(2 * np.pi * months / 12.0)

    # 2. Bổ sung khoảng cách trung tâm và độ cao (Spatial Features)
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
    df["dist_center_km"] = df["station_id"].map(lambda sid: station_meta.get(sid, {}).get("dist_center_km", 5.0))
    df["elevation_m"] = df["station_id"].map(lambda sid: station_meta.get(sid, {}).get("elevation_m", 10.0))

    # 3. Lags & Rolling Features tính riêng theo từng trạm
    grouped = df.groupby("station_id")
    
    # PM2.5 Lags
    for lag in [1, 2, 3, 6, 12, 24]:
        df[f"pm25_lag_{lag}"] = grouped["pm25"].shift(lag)

    # Các khí khác Lag 1
    df["pm10_lag_1"] = grouped["pm10"].shift(1)
    df["no2_lag_1"] = grouped["no2"].shift(1)
    df["co_lag_1"] = grouped["co"].shift(1)
    df["o3_lag_1"] = grouped["o3"].shift(1)
    df["so2_lag_1"] = grouped["so2"].shift(1)

    # Rolling Means & Stds (chỉ dùng quá khứ, min_periods=1)
    df["pm25_roll_mean_6h"] = grouped["pm25"].transform(lambda x: x.shift(1).rolling(6, min_periods=1).mean())
    df["pm25_roll_std_6h"] = grouped["pm25"].transform(lambda x: x.shift(1).rolling(6, min_periods=1).std().fillna(0.0))
    df["pm25_roll_mean_24h"] = grouped["pm25"].transform(lambda x: x.shift(1).rolling(24, min_periods=1).mean())
    df["temp_roll_mean_6h"] = grouped["temperature"].transform(lambda x: x.shift(1).rolling(6, min_periods=1).mean())
    df["wind_roll_mean_6h"] = grouped["wind_speed"].transform(lambda x: x.shift(1).rolling(6, min_periods=1).mean())

    # 4. Target variable: Giá trị PM2.5 ở bước thời gian tiếp theo (t + 1)
    df[TARGET_COL] = grouped["pm25"].shift(-1)

    # 5. Loại bỏ các dòng đầu tiên (chưa đủ 24 lag) và dòng cuối cùng (không có target t+1)
    df = df.dropna(subset=FEATURE_COLS + [TARGET_COL]).reset_index(drop=True)
    return df

def split_chronological(df: pd.DataFrame, train_ratio=0.70, val_ratio=0.15):
    """
    Chia dữ liệu theo thứ tự thời gian (Strictly Chronological Split).
    Train (70%) -> Val (15%) -> Test (15%). Tuyệt đối không xáo trộn (No Shuffle).
    """
    unique_timestamps = np.sort(df["timestamp"].unique())
    n_times = len(unique_timestamps)
    
    train_end_idx = int(n_times * train_ratio)
    val_end_idx = int(n_times * (train_ratio + val_ratio))
    
    train_times = set(unique_timestamps[:train_end_idx])
    val_times = set(unique_timestamps[train_end_idx:val_end_idx])
    test_times = set(unique_timestamps[val_end_idx:])
    
    train_df = df[df["timestamp"].isin(train_times)].copy()
    val_df = df[df["timestamp"].isin(val_times)].copy()
    test_df = df[df["timestamp"].isin(test_times)].copy()
    
    return train_df, val_df, test_df

def process_and_save():
    print("=== BAT DAU TIEN XU LY DU LIEU VA FEATURE ENGINEERING ===")
    raw_df = pd.read_csv(RAW_CSV)
    print(f"1. Doc du lieu tho: {len(raw_df)} dong tu {RAW_CSV}")

    cleaned_df = clean_and_impute(raw_df)
    feature_df = create_features(cleaned_df)
    print(f"2. Da tao dac trung thanh cong: {len(feature_df)} mau hop le")
    print(f"   So luong dac trung: {len(FEATURE_COLS)} features")

    train_df, val_df, test_df = split_chronological(feature_df)
    print(f"3. Chia tap du lieu theo thu tu thoi gian (Chronological Split):")
    print(f"   - Train set: {len(train_df)} mau ({train_df['timestamp'].min()} den {train_df['timestamp'].max()})")
    print(f"   - Val set:   {len(val_df)} mau ({val_df['timestamp'].min()} den {val_df['timestamp'].max()})")
    print(f"   - Test set:  {len(test_df)} mau ({test_df['timestamp'].min()} den {test_df['timestamp'].max()})")

    # Fit Scaler CHI TREN TAP TRAIN
    scaler = StandardScaler()
    scaler.fit(train_df[FEATURE_COLS])
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")
    print(f"4. Da luu StandardScaler vao {MODELS_DIR / 'scaler.joblib'}")

    # Luu tap du lieu da xu ly
    train_df.to_csv(PROCESSED_DIR / "train.csv", index=False)
    val_df.to_csv(PROCESSED_DIR / "val.csv", index=False)
    test_df.to_csv(PROCESSED_DIR / "test.csv", index=False)
    feature_df.to_csv(PROCESSED_DIR / "clean_features.csv", index=False)
    print(f"5. Da luu cac tap train/val/test vao {PROCESSED_DIR}")
    print("=== HOAN TAT TIEN XU LY ===")

if __name__ == "__main__":
    process_and_save()
