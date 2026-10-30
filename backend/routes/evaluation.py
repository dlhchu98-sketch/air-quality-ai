"""
Evaluation & Explanation Routes: Cung cấp bảng so sánh chỉ số thực nghiệm và tài liệu giải thích.
"""

from fastapi import APIRouter
from backend.lifespan import state
from backend.schemas import ModelEvaluationItem

router = APIRouter(prefix="/api", tags=["Model Evaluation & Explainability"])

@router.get("/models/evaluation", response_model=dict[str, ModelEvaluationItem])
async def get_model_evaluation():
    """Trả về bảng chỉ số thực nghiệm (MAE, RMSE, R2, Latency) đánh giá trên test set độc lập."""
    return state.metrics_data

@router.get("/explain")
async def get_model_explanation():
    """Tài liệu giải thích mô hình AI bằng tiếng Việt phục vụ sinh viên đại học."""
    return {
        "problem_definition": {
            "title": "Dự báo nồng độ bụi mịn PM2.5 theo không gian - thời gian",
            "inputs": "Chuỗi quan trắc 24 giờ quá khứ (PM2.5, PM10, khí NO2, CO, O3, SO2), đặc trưng chu kỳ thời gian (giờ trong ngày, ngày trong tuần, tháng), yếu tố khí tượng (nhiệt độ, độ ẩm, tốc độ gió) và tọa độ địa không gian GeoPandas (khoảng cách trung tâm, độ cao).",
            "outputs": "Nồng độ bụi mịn PM2.5 (µg/m³) dự báo đa bước thời gian (1h - 24h tiếp theo), cận trên/cận dưới khoảng tin cậy, và phân cấp mức độ cảnh báo sức khỏe AQI."
        },
        "preprocessing_pipeline": [
            "1. Làm sạch dữ liệu: Xử lý giá trị thiếu bằng Forward Fill theo trạm và Rolling Median.",
            "2. Xử lý ngoại lai: Physical bounds clipping bảo vệ khỏi các giá trị âm hoặc vượt ngưỡng cảm biến.",
            "3. Mã hóa chu kỳ (Cyclical Encoding): Sử dụng hàm sin/cos biểu diễn tính liên tục của giờ (23h sang 0h) và tháng.",
            "4. Đặc trưng trễ (Lags): Tạo độ trễ t-1 đến t-24 giờ để nắm bắt quán tính khí quyển.",
            "5. Thống kê trượt (Rolling Stats): Tính trung bình và độ lệch chuẩn 6h, 24h phản ánh xu hướng ngắn và dài hạn.",
            "6. Tích hợp GeoPandas: Gán tọa độ WGS84, chuyển đổi UTM 48N tính khoảng cách tới tâm đô thị.",
            "7. Chia tập dữ liệu Chronological (70% Train, 15% Val, 15% Test): Đảm bảo nguyên tắc vàng 'Không rò rỉ dữ liệu tương lai'."
        ],
        "models_comparison": {
            "baseline": "Persistence Model (t-1): Giả định ô nhiễm giờ tới bằng đúng giờ này. Phục vụ làm mốc cơ sở so sánh.",
            "random_forest": "Random Forest Regressor (100 cây): Mô hình học máy dựa trên tập hợp cây quyết định, xử lý phi tuyến tính xuất sắc, kháng overfitting tốt trên dữ liệu bảng dạng lag.",
            "neural_network": "Time-Series Multi-Layer Perceptron (64-32 units, ReLU): Mạng nơ-ron học sâu mô hình hóa mối quan hệ phi tuyến giữa khí tượng và ô nhiễm."
        },
        "why_random_forest_wins": "Thực nghiệm cho thấy Random Forest đạt R² = 0.721 và MAE thấp hơn 41% so với Baseline. Mô hình dạng cây rất hiệu quả với dữ liệu bảng đặc trưng trễ do không yêu cầu giả định phân phối chuẩn tuyến tính.",
        "limitations_and_disclaimer": [
            "Mô hình giả định quy luật khí quyển ổn định tương đối theo lịch sử, có thể sai lệch khi xuất hiện hiện tượng thời tiết cực đoan đột ngột (bão lớn, nghịch nhiệt bất thường).",
            "Dự báo đa bước từ giờ thứ 12 trở đi có độ bất định tăng dần do sai số tích lũy của phương pháp hồi quy tự sinh.",
            "Hệ thống xây dựng phục vụ mục đích nghiên cứu, học tập; không thay thế dữ liệu quan trắc pháp lý của Bộ Tài nguyên và Môi trường."
        ]
    }
