"""
Unit test kiểm thử nạp mô hình và suy luận dự báo chuỗi thời gian.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.inference import ForecastEngine, calculate_aqi_category

def test_models_exist_and_load():
    models_dir = BASE_DIR / "models"
    assert (models_dir / "baseline.joblib").exists(), "Thieu file baseline.joblib"
    assert (models_dir / "random_forest.joblib").exists(), "Thieu file random_forest.joblib"
    assert (models_dir / "neural_forecast.joblib").exists(), "Thieu file neural_forecast.joblib"
    assert (models_dir / "scaler.joblib").exists(), "Thieu file scaler.joblib"
    assert (models_dir / "metrics.json").exists(), "Thieu file metrics.json"

    engine = ForecastEngine(models_dir)
    assert engine.rf is not None
    assert engine.neural is not None
    assert engine.baseline is not None

def test_inference_multistep():
    models_dir = BASE_DIR / "models"
    engine = ForecastEngine(models_dir)

    # Tạo DataFrame giả lập 30 giờ gần nhất của 1 trạm
    now = pd.Timestamp.now()
    times = [now - pd.Timedelta(hours=i) for i in reversed(range(30))]
    sample_df = pd.DataFrame({
        "timestamp": times,
        "station_id": ["VN_HN_01"] * 30,
        "station_name": ["Trạm Hoàn Kiếm"] * 30,
        "district": ["Hoàn Kiếm"] * 30,
        "pm25": np.random.uniform(25.0, 60.0, 30),
        "pm10": np.random.uniform(40.0, 90.0, 30),
        "no2": np.random.uniform(15.0, 35.0, 30),
        "co": np.random.uniform(0.5, 1.5, 30),
        "o3": np.random.uniform(20.0, 50.0, 30),
        "so2": np.random.uniform(5.0, 15.0, 30),
        "temperature": np.random.uniform(22.0, 32.0, 30),
        "humidity": np.random.uniform(60.0, 85.0, 30),
        "wind_speed": np.random.uniform(1.0, 4.0, 30),
        "dist_center_km": [0.0] * 30,
        "elevation_m": [12.0] * 30
    })

    for model_name in ["Random_Forest", "Neural_Network", "Baseline"]:
        results = engine.forecast_multistep(sample_df, model_name=model_name, horizon_hours=12)
        assert len(results) == 12, f"Phai tra ve dung 12 buoc du bao cho {model_name}"
        for step in results:
            assert step["pm25_predicted"] > 0, "Gia tri PM2.5 phai > 0"
            assert step["lower_bound"] <= step["pm25_predicted"] <= step["upper_bound"], "Khoang tin cay sai logic"
            assert "aqi_level" in step
            assert "health_advice" in step

def test_aqi_categorization():
    cat_good = calculate_aqi_category(10.0)
    assert cat_good["aqi_code"] == "GOOD"
    assert cat_good["color"] == "#10b981"

    cat_unhealthy = calculate_aqi_category(80.0)
    assert cat_unhealthy["aqi_code"] == "UNHEALTHY"
    assert cat_unhealthy["color"] == "#ef4444"
