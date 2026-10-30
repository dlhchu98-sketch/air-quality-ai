"""
Air Quality Routes: Dữ liệu quan trắc mới nhất, lịch sử chuỗi thời gian, và API Dự báo AI.
"""

from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from backend.lifespan import state
from backend.schemas import (
    LatestObservation,
    ForecastRequest,
    ForecastResponse,
    ForecastStepResult
)
from ml.inference import calculate_aqi_category

router = APIRouter(prefix="/api/air-quality", tags=["Air Quality & Forecasting"])

@router.get("/latest", response_model=list[LatestObservation])
async def get_latest_observations():
    """Trả về quan trắc mới nhất tại toàn bộ 8 trạm trên bản đồ."""
    state.ensure_started()
    latest_df = state.history_df.sort_values("timestamp").groupby("station_id").last().reset_index()
    results = []
    for _, row in latest_df.iterrows():
        aqi_info = calculate_aqi_category(float(row["pm25"]))
        results.append({
            "station_id": row["station_id"],
            "station_name": row["station_name"],
            "district": row["district"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "timestamp": pd.to_datetime(row["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
            "pm25": float(row["pm25"]),
            "pm10": float(row["pm10"]),
            "no2": float(row["no2"]),
            "co": float(row["co"]),
            "o3": float(row["o3"]),
            "so2": float(row["so2"]),
            "temperature": float(row["temperature"]),
            "humidity": float(row["humidity"]),
            "wind_speed": float(row["wind_speed"]),
            "aqi_level": aqi_info["aqi_level"],
            "aqi_code": aqi_info["aqi_code"],
            "color": aqi_info["color"]
        })
    return results

@router.get("/history")
async def get_station_history(
    station_id: str = Query("VN_HN_01", description="Mã trạm"),
    pollutant: str = Query("pm25", description="Chỉ số quan trắc (pm25, pm10, no2, co, o3, so2)"),
    hours: int = Query(72, ge=6, le=168, description="Số giờ lịch sử cần lấy (6 đến 168 giờ)")
):
    """Lấy dữ liệu lịch sử cho biểu đồ phân tích chuỗi thời gian."""
    state.ensure_started()
    station_data = state.history_df[state.history_df["station_id"] == station_id].sort_values("timestamp")
    if station_data.empty:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy trạm có mã '{station_id}'")

    recent = station_data.tail(hours)
    
    records = []
    for _, row in recent.iterrows():
        val = float(row.get(pollutant, row["pm25"]))
        records.append({
            "timestamp": pd.to_datetime(row["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
            "value": round(val, 2),
            "temperature": float(row.get("temperature", 25.0)),
            "humidity": float(row.get("humidity", 70.0)),
            "wind_speed": float(row.get("wind_speed", 2.0))
        })
    
    return {
        "station_id": station_id,
        "station_name": station_data.iloc[0]["station_name"],
        "pollutant": pollutant,
        "hours": hours,
        "records": records
    }

@router.post("/forecast", response_model=ForecastResponse)
async def forecast_air_quality(req: ForecastRequest):
    """
    API DỰ BÁO CHẤT LƯỢNG KHÔNG KHÍ THỰC TẾ:
    - Nạp dữ liệu trễ thực tế từ bộ nhớ.
    - Chạy mô hình AI đã chọn (Baseline, Random Forest, Neural Network).
    - Dự báo đa bước thời gian (1h đến 24h) không gây rò rỉ dữ liệu tương lai.
    - Trả về kết quả dự báo, khoảng tin cậy và khuyến nghị y tế.
    """
    state.ensure_started()
    station_data = state.history_df[state.history_df["station_id"] == req.station_id].sort_values("timestamp")
    if station_data.empty:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy trạm '{req.station_id}'")

    # Lấy 48 giờ gần nhất để làm chuỗi lịch sử đầu vào cho engine
    recent_history = station_data.tail(48)
    
    # Thực hiện suy luận
    forecast_steps_data = state.engine.forecast_multistep(
        recent_history=recent_history,
        model_name=req.model_name,
        horizon_hours=req.horizon_hours
    )

    last_record = recent_history.iloc[-1]
    
    return {
        "station_id": req.station_id,
        "station_name": last_record["station_name"],
        "district": last_record["district"],
        "model_used": req.model_name,
        "horizon_hours": req.horizon_hours,
        "current_timestamp": pd.to_datetime(last_record["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
        "current_pm25": float(last_record["pm25"]),
        "forecast_steps": [ForecastStepResult(**s) for s in forecast_steps_data],
        "disclaimer": "Dự báo bởi mô hình AI phục vụ học tập, nghiên cứu và tham khảo. Không tuyên bố là số liệu quan trắc thực tế."
    }
