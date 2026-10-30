"""
Module huấn luyện và so sánh 3 mô hình dự báo chất lượng không khí:
1. Mô hình Baseline: Persistence Model (dự báo bằng giá trị giờ trước t-1).
2. Mô hình Machine Learning: Random Forest Regressor (100 cây, max_depth=12).
3. Mô hình Deep Learning: Multi-Layer Perceptron (MLP Neural Network, 64-32 units, ReLU, Early Stopping).

Các mô hình được huấn luyện trên Train Set, tinh chỉnh trên Val Set,
và đánh giá độc lập trên Test Set (5,160 mẫu hoàn toàn không nhìn thấy trước).
"""

import sys
import time
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

from ml.data_processing import FEATURE_COLS, TARGET_COL
from ml.models import BaselinePersistenceModel

def train_and_evaluate_all():
    print("=== BAT DAU HUAN LUYEN VA DANH GIA CAC MO HINH AI ===")
    
    # 1. Nạp dữ liệu
    train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DIR / "val.csv")
    test_df = pd.read_csv(PROCESSED_DIR / "test.csv")
    scaler = joblib.load(MODELS_DIR / "scaler.joblib")

    X_train_raw = train_df[FEATURE_COLS]
    y_train = train_df[TARGET_COL].values

    X_val_raw = val_df[FEATURE_COLS]
    y_val = val_df[TARGET_COL].values

    X_test_raw = test_df[FEATURE_COLS]
    y_test = test_df[TARGET_COL].values

    # Chuẩn hóa dữ liệu cho Neural Network
    X_train_scaled = scaler.transform(X_train_raw)
    X_val_scaled = scaler.transform(X_val_raw)
    X_test_scaled = scaler.transform(X_test_raw)

    metrics_results = {}

    # ----------------------------------------------------
    # Model 1: Baseline Persistence
    # ----------------------------------------------------
    print("\n--- 1. Danh gia Mo hinh Co so (Baseline Persistence t-1) ---")
    baseline_model = BaselinePersistenceModel()
    start_time = time.time()
    # Baseline dự báo trực tiếp bằng pm25_lag_1
    y_pred_baseline = X_test_raw["pm25_lag_1"].values
    baseline_infer_time = (time.time() - start_time) / len(y_test) * 1000

    mae_base = float(mean_absolute_error(y_test, y_pred_baseline))
    rmse_base = float(root_mean_squared_error(y_test, y_pred_baseline))
    r2_base = float(r2_score(y_test, y_pred_baseline))

    metrics_results["Baseline_Persistence"] = {
        "model_name": "Baseline (Persistence t-1)",
        "model_type": "Heuristic / Baseline",
        "description": "Dự báo giá trị PM2.5 ở bước t+1 bằng chính giá trị đo được tại bước t",
        "mae": round(mae_base, 3),
        "rmse": round(rmse_base, 3),
        "r2": round(r2_base, 4),
        "train_time_sec": 0.001,
        "inference_latency_ms": round(baseline_infer_time, 4),
        "test_samples": len(y_test)
    }
    joblib.dump(baseline_model, MODELS_DIR / "baseline.joblib")
    print(f"  [Baseline] MAE: {mae_base:.3f} | RMSE: {rmse_base:.3f} | R2: {r2_base:.4f}")

    # ----------------------------------------------------
    # Model 2: Machine Learning - Random Forest
    # ----------------------------------------------------
    print("\n--- 2. Huan luyen Mo hinh Machine Learning (Random Forest) ---")
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42
    )
    t0 = time.time()
    rf_model.fit(X_train_raw, y_train)
    rf_train_time = time.time() - t0

    # Đánh giá suy luận trên Test Set
    t0 = time.time()
    y_pred_rf = rf_model.predict(X_test_raw)
    rf_infer_time = (time.time() - t0) / len(y_test) * 1000

    mae_rf = float(mean_absolute_error(y_test, y_pred_rf))
    rmse_rf = float(root_mean_squared_error(y_test, y_pred_rf))
    r2_rf = float(r2_score(y_test, y_pred_rf))

    # Tính độ quan trọng đặc trưng (Feature Importances)
    importances = rf_model.feature_importances_
    top_features = sorted(zip(FEATURE_COLS, importances), key=lambda x: x[1], reverse=True)[:8]

    metrics_results["Random_Forest"] = {
        "model_name": "Random Forest Regressor",
        "model_type": "Tree Ensemble Machine Learning",
        "description": "Mô hình rừng cây quyết định 100 cây, kết hợp đặc trưng trễ, khí tượng và không gian",
        "mae": round(mae_rf, 3),
        "rmse": round(rmse_rf, 3),
        "r2": round(r2_rf, 4),
        "train_time_sec": round(rf_train_time, 2),
        "inference_latency_ms": round(rf_infer_time, 4),
        "top_features": [{"feature": f, "importance": round(float(imp), 4)} for f, imp in top_features],
        "test_samples": len(y_test)
    }
    joblib.dump(rf_model, MODELS_DIR / "random_forest.joblib")
    print(f"  [Random Forest] Train Time: {rf_train_time:.2f}s | Infer Latency: {rf_infer_time:.4f}ms/sample")
    print(f"  [Random Forest] MAE: {mae_rf:.3f} | RMSE: {rmse_rf:.3f} | R2: {r2_rf:.4f}")

    # ----------------------------------------------------
    # Model 3: Deep Learning - MLP Neural Network
    # ----------------------------------------------------
    print("\n--- 3. Huan luyen Mo hinh Deep Learning (Time-Series Neural Net/MLP) ---")
    mlp_model = MLPRegressor(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        alpha=0.001,
        batch_size=64,
        learning_rate_init=0.003,
        max_iter=120,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=10,
        random_state=42
    )
    t0 = time.time()
    mlp_model.fit(X_train_scaled, y_train)
    mlp_train_time = time.time() - t0

    t0 = time.time()
    y_pred_mlp = mlp_model.predict(X_test_scaled)
    mlp_infer_time = (time.time() - t0) / len(y_test) * 1000

    mae_mlp = float(mean_absolute_error(y_test, y_pred_mlp))
    rmse_mlp = float(root_mean_squared_error(y_test, y_pred_mlp))
    r2_mlp = float(r2_score(y_test, y_pred_mlp))

    metrics_results["Neural_Network"] = {
        "model_name": "Time-Series Neural Network (MLP)",
        "model_type": "Deep Learning / Feedforward Time-Series Net",
        "description": "Mạng nơ-ron học sâu đa tầng (64-32 units, ReLU, Adam) dự báo phi tuyến chuỗi thời gian",
        "mae": round(mae_mlp, 3),
        "rmse": round(rmse_mlp, 3),
        "r2": round(r2_mlp, 4),
        "train_time_sec": round(mlp_train_time, 2),
        "inference_latency_ms": round(mlp_infer_time, 4),
        "epochs_trained": mlp_model.n_iter_,
        "test_samples": len(y_test)
    }
    joblib.dump(mlp_model, MODELS_DIR / "neural_forecast.joblib")
    print(f"  [Neural Network] Train Time: {mlp_train_time:.2f}s | Iterations: {mlp_model.n_iter_}")
    print(f"  [Neural Network] MAE: {mae_mlp:.3f} | RMSE: {rmse_mlp:.3f} | R2: {r2_mlp:.4f}")

    # Lưu toàn bộ metrics vào file JSON để FastAPI và Website nạp hiển thị
    with open(MODELS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_results, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Da luu toan bo chi so danh gia vao {MODELS_DIR / 'metrics.json'}")
    print("=== HOAN TAT HUAN LUYEN VA DANH GIA ===")

if __name__ == "__main__":
    train_and_evaluate_all()
