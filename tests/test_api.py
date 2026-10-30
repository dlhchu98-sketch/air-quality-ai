"""
Integration test kiểm thử các API endpoint của FastAPI.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app import app
from backend.lifespan import state

state.ensure_started()
client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "memory_mb" in data
    assert data["stations_count"] == 8
    assert data["districts_count"] == 8

def test_api_stations():
    res = client.get("/api/stations")
    assert res.status_code == 200
    stations = res.json()
    assert len(stations) == 8
    first = stations[0]
    assert "station_id" in first
    assert "latitude" in first
    assert "longitude" in first

def test_api_regions_geojson():
    res = client.get("/api/regions")
    assert res.status_code == 200
    geojson = res.json()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 8
    assert "pm25" in geojson["features"][0]["properties"]
    assert "aqi_level" in geojson["features"][0]["properties"]

def test_api_latest_air_quality():
    res = client.get("/api/air-quality/latest")
    assert res.status_code == 200
    latest = res.json()
    assert len(latest) == 8
    for obs in latest:
        assert obs["pm25"] > 0
        assert "aqi_level" in obs

def test_api_history():
    res = client.get("/api/air-quality/history?station_id=VN_HN_01&hours=24")
    assert res.status_code == 200
    data = res.json()
    assert data["station_id"] == "VN_HN_01"
    assert len(data["records"]) <= 24

def test_api_forecast():
    payload = {
        "station_id": "VN_HN_01",
        "pollutant": "pm25",
        "model_name": "Random_Forest",
        "horizon_hours": 6
    }
    res = client.post("/api/air-quality/forecast", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["station_id"] == "VN_HN_01"
    assert data["model_used"] == "Random_Forest"
    assert len(data["forecast_steps"]) == 6
    assert data["forecast_steps"][0]["step_ahead"] == 1

def test_api_evaluation_metrics():
    res = client.get("/api/models/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert "Random_Forest" in data
    assert "Baseline_Persistence" in data
    assert "Neural_Network" in data
    assert data["Random_Forest"]["r2"] > 0.5
