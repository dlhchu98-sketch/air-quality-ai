"""
Engine suy luận dự báo chất lượng không khí (Inference Engine).
Chức năng:
1. Nạp mô hình (Baseline, Random Forest, Neural Network) và StandardScaler từ bộ nhớ.
2. Thực hiện dự báo đa bước thời gian (Multi-step autoregressive forecasting) từ 1h đến 24h.
3. Tính toán khoảng tin cậy (Confidence Interval +/- 10-15%).
4. Phân loại chỉ số AQI chuẩn quốc tế EPA / VN_AQI (Tốt, Trung bình, Kém, Xấu, Rất xấu, Nguy hại) và đưa ra khuyến nghị y tế.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
import joblib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.data_processing import FEATURE_COLS
from ml.models import BaselinePersistenceModel

def calculate_aqi_category(pm25_val: float) -> dict:
    """
    Quy đổi nồng độ PM2.5 (ug/m3) theo bảng phân cấp AQI chuẩn EPA / QCVN:
    0 - 12: Tốt (Good - Xanh lá)
    12.1 - 35.4: Trung bình (Moderate - Vàng)
    35.5 - 55.4: Kém / Nhạy cảm (Unhealthy for Sensitive Groups - Cam)
    55.5 - 150.4: Xấu (Unhealthy - Đỏ)
    150.5 - 250.4: Rất xấu (Very Unhealthy - Tím)
    > 250.4: Nguy hại (Hazardous - Nâu đỏ)
    """
    if pm25_val <= 12.0:
        return {
            "aqi_level": "Tốt",
            "aqi_code": "GOOD",
            "color": "#10b981", # Green
            "health_advice": "Chất lượng không khí đạt chuẩn an toàn, lý tưởng cho mọi hoạt động ngoài trời."
        }
    elif pm25_val <= 35.4:
        return {
            "aqi_level": "Trung bình",
            "aqi_code": "MODERATE",
            "color": "#f59e0b", # Yellow / Amber
            "health_advice": "Chất lượng không khí ở mức chấp nhận được. Nhóm người đặc biệt nhạy cảm nên hạn chế hoạt động mạnh ngoài trời kéo dài."
        }
    elif pm25_val <= 55.4:
        return {
            "aqi_level": "Kém cho nhóm nhạy cảm",
            "aqi_code": "USG",
            "color": "#f97316", # Orange
            "health_advice": "Trẻ em, người già và người mắc bệnh hô hấp nên giảm tiếp xúc với không khí bên ngoài."
        }
    elif pm25_val <= 150.4:
        return {
            "aqi_level": "Xấu",
            "aqi_code": "UNHEALTHY",
            "color": "#ef4444", # Red
            "health_advice": "Tất cả mọi người bắt đầu cảm nhận ảnh hưởng sức khỏe. Nên đeo khẩu trang chống bụi mịn N95 khi ra ngoài."
        }
    elif pm25_val <= 250.4:
        return {
            "aqi_level": "Rất xấu",
            "aqi_code": "VERY_UNHEALTHY",
            "color": "#8b5cf6", # Purple
            "health_advice": "Cảnh báo khẩn cấp về sức khỏe. Tránh các hoạt động gắng sức ngoài trời, đóng kín cửa sổ và bật máy lọc không khí."
        }
    else:
        return {
            "aqi_level": "Nguy hại",
            "aqi_code": "HAZARDOUS",
            "color": "#881337", # Maroon
            "health_advice": "Mức độ ô nhiễm nghiêm trọng ảnh hưởng trực tiếp tới toàn bộ dân số. Tuyệt đối không ra ngoài nếu không thực sự cần thiết."
        }

class ForecastEngine:
    """Quản lý các mô hình và suy luận đa bước thời gian."""
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.scaler = joblib.load(models_dir / "scaler.joblib")
        self.baseline = joblib.load(models_dir / "baseline.joblib")
        self.rf = joblib.load(models_dir / "random_forest.joblib")
        self.neural = joblib.load(models_dir / "neural_forecast.joblib")
        
    def forecast_multistep(
        self,
        recent_history: pd.DataFrame,
        model_name: str = "Random_Forest",
        horizon_hours: int = 12
    ) -> list[dict]:
        """
        Dự báo hồi quy đa bước (Multi-step autoregressive forecasting) cho các giờ tiếp theo.
        Không sử dụng dữ liệu rò rỉ từ tương lai: mỗi bước t+k sử dụng kết quả dự báo ở bước t+k-1
        để cập nhật lại vector đặc trưng trễ (lags).
        """
        model_name_lower = model_name.lower()
        horizon_hours = min(max(horizon_hours, 1), 24)

        # Lấy bản ghi cuối cùng của lịch sử làm trạng thái gốc t_0
        last_row = recent_history.iloc[-1].copy()
        current_time = pd.to_datetime(last_row["timestamp"])
        
        # Buffer lưu trữ chuỗi PM2.5 quá khứ gần nhất (đủ 24 bước để cập nhật lag)
        pm25_buffer = recent_history["pm25"].tail(24).tolist()
        if len(pm25_buffer) < 24:
            # Nếu lịch sử ít hơn 24 giờ, mở rộng bằng giá trị trung bình
            pm25_buffer = [last_row["pm25"]] * (24 - len(pm25_buffer)) + pm25_buffer

        results = []
        
        for step in range(1, horizon_hours + 1):
            future_time = current_time + pd.Timedelta(hours=step)
            hour = future_time.hour
            dow = future_time.weekday()
            month = future_time.month

            # 1. Cập nhật đặc trưng chu kỳ thời gian
            sin_hour = np.sin(2 * np.pi * hour / 24.0)
            cos_hour = np.cos(2 * np.pi * hour / 24.0)
            sin_dow = np.sin(2 * np.pi * dow / 7.0)
            cos_dow = np.cos(2 * np.pi * dow / 7.0)
            sin_month = np.sin(2 * np.pi * month / 12.0)
            cos_month = np.cos(2 * np.pi * month / 12.0)

            # 2. Cập nhật lags từ pm25_buffer (tương lai tự sinh)
            pm25_lag_1 = pm25_buffer[-1]
            pm25_lag_2 = pm25_buffer[-2]
            pm25_lag_3 = pm25_buffer[-3]
            pm25_lag_6 = pm25_buffer[-6]
            pm25_lag_12 = pm25_buffer[-12]
            pm25_lag_24 = pm25_buffer[-24]

            # 3. Rolling stats tự sinh từ buffer
            pm25_roll_mean_6h = np.mean(pm25_buffer[-6:])
            pm25_roll_std_6h = float(np.std(pm25_buffer[-6:]))
            pm25_roll_mean_24h = np.mean(pm25_buffer[-24:])

            # 4. Dự báo các yếu tố khí tượng tương đối theo chu kỳ ngày
            temp_est = float(last_row["temperature"] + 4.0 * np.sin(np.pi * (hour - 9) / 12))
            humidity_est = float(np.clip(last_row["humidity"] - 8.0 * np.sin(np.pi * (hour - 9) / 12), 35.0, 98.0))
            wind_est = float(last_row["wind_speed"])

            feature_dict = {
                "sin_hour": sin_hour,
                "cos_hour": cos_hour,
                "sin_dow": sin_dow,
                "cos_dow": cos_dow,
                "sin_month": sin_month,
                "cos_month": cos_month,
                "temperature": temp_est,
                "humidity": humidity_est,
                "wind_speed": wind_est,
                "pm25_lag_1": pm25_lag_1,
                "pm25_lag_2": pm25_lag_2,
                "pm25_lag_3": pm25_lag_3,
                "pm25_lag_6": pm25_lag_6,
                "pm25_lag_12": pm25_lag_12,
                "pm25_lag_24": pm25_lag_24,
                "pm10_lag_1": float(last_row.get("pm10", pm25_lag_1 * 1.4)),
                "no2_lag_1": float(last_row.get("no2", 25.0)),
                "co_lag_1": float(last_row.get("co", 1.0)),
                "o3_lag_1": float(last_row.get("o3", 30.0)),
                "so2_lag_1": float(last_row.get("so2", 10.0)),
                "pm25_roll_mean_6h": pm25_roll_mean_6h,
                "pm25_roll_std_6h": pm25_roll_std_6h,
                "pm25_roll_mean_24h": pm25_roll_mean_24h,
                "temp_roll_mean_6h": temp_est,
                "wind_roll_mean_6h": wind_est,
                "dist_center_km": float(last_row.get("dist_center_km", 3.0)),
                "elevation_m": float(last_row.get("elevation_m", 12.0))
            }

            feat_df = pd.DataFrame([feature_dict])[FEATURE_COLS]

            # 5. Suy luận theo mô hình được chỉ định
            if "baseline" in model_name_lower:
                pred_val = float(pm25_lag_1)
            elif "neural" in model_name_lower or "mlp" in model_name_lower:
                scaled_x = self.scaler.transform(feat_df)
                pred_val = float(self.neural.predict(scaled_x)[0])
            else: # Random Forest mặc định
                pred_val = float(self.rf.predict(feat_df)[0])

            # Giới hạn vật lý không âm
            pred_val = max(5.0, round(pred_val, 2))
            
            # Cập nhật buffer cho các bước tiếp theo
            pm25_buffer.append(pred_val)

            # Khoảng không chắc chắn tăng dần theo horizon (uncertainty grows with horizon)
            uncertainty = round(pred_val * (0.05 + 0.008 * step), 2)
            lower_bound = max(0.0, round(pred_val - uncertainty, 2))
            upper_bound = round(pred_val + uncertainty, 2)

            aqi_meta = calculate_aqi_category(pred_val)

            results.append({
                "step_ahead": step,
                "forecast_time": future_time.strftime("%Y-%m-%d %H:%M:%S"),
                "pm25_predicted": pred_val,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "unit": "µg/m³",
                "aqi_level": aqi_meta["aqi_level"],
                "aqi_code": aqi_meta["aqi_code"],
                "color": aqi_meta["color"],
                "health_advice": aqi_meta["health_advice"]
            })

        return results
