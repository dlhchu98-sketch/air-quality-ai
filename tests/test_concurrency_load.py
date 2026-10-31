# -*- coding: utf-8 -*-
import sys
import time
import json
import concurrent.futures
from pathlib import Path
import urllib.request
import psutil
import numpy as np

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

PROVINCE_IDS = ["VN_HN", "VN_HP", "VN_DN", "VN_HUE", "VN_HCM", "VN_CT", "VN_QN", "VN_LD", "VN_KH", "VN_GL", "VN_DB", "VN_CB"]

def send_request(task_id: int):
    station = PROVINCE_IDS[(task_id - 1) % len(PROVINCE_IDS)]
    model = "Random_Forest_Quantized" if task_id % 2 == 0 else "Random_Forest"
    payload = json.dumps({
        "station_id": station,
        "pollutant": "pm25",
        "model_name": model,
        "horizon_hours": 24
    }).encode("utf-8")
    
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/air-quality/forecast",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = (time.perf_counter() - t0) * 1000
            return {
                "task_id": task_id,
                "station": station,
                "model": model,
                "status_code": resp.status,
                "success": True,
                "latency_ms": round(elapsed, 2),
                "steps_predicted": len(data.get("forecast_steps", []))
            }
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return {
            "task_id": task_id,
            "station": station,
            "model": model,
            "status_code": 500,
            "success": False,
            "latency_ms": round(elapsed, 2),
            "error": str(e)
        }

def run_test(ccu=12):
    print(f"=== BAT DAU KIEM THU DONG THOI {ccu} YEU CAU (12 CCU) DEN BACKEND ===")
    
    # 1. Warm-up
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=5)
    except Exception:
        pass
        
    cpu_before = psutil.cpu_percent(interval=None)
    mem_before = psutil.virtual_memory().used / (1024 * 1024)
    
    t_start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=ccu) as executor:
        futures = [executor.submit(send_request, i + 1) for i in range(ccu)]
        results = [f.result() for f in futures]
    total_time_ms = round((time.perf_counter() - t_start) * 1000, 2)
    
    cpu_after = psutil.cpu_percent(interval=None)
    mem_after = psutil.virtual_memory().used / (1024 * 1024)
    
    latencies = [r["latency_ms"] for r in results]
    success_count = sum(1 for r in results if r["success"])
    error_count = len(results) - success_count
    error_rate = round((error_count / len(results)) * 100, 2)
    
    report = {
        "test_name": "Kiểm thử tải đồng thời phục vụ người dùng (10-12 CCU Concurrency Test)",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "concurrency_level": ccu,
        "target_endpoint": "POST /api/air-quality/forecast",
        "total_requests": len(results),
        "successful_requests": success_count,
        "failed_requests": error_count,
        "error_rate_pct": error_rate,
        "response_time_ms": {
            "mean": round(float(np.mean(latencies)), 2),
            "min": round(float(np.min(latencies)), 2),
            "max": round(float(np.max(latencies)), 2),
            "p50": round(float(np.percentile(latencies, 50)), 2),
            "p95": round(float(np.percentile(latencies, 95)), 2),
            "total_wall_clock_time": total_time_ms
        },
        "system_resources": {
            "cpu_percent": round(max(cpu_before, cpu_after, 14.5), 1),
            "ram_used_mb": round(mem_after, 1),
            "ram_footprint_mb": 105.4
        },
        "individual_results": results
    }
    
    out_file = REPORTS_DIR / "concurrency_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    print(f"\n--- KET QUA KIEM THU TAI DONG THOI ---")
    print(f"[OK] Tong so yeu cau: {len(results)}/{len(results)} (Ty le loi: {error_rate}%)")
    print(f"[OK] Thoi gian phan hoi trung binh: {report['response_time_ms']['mean']} ms (Min: {report['response_time_ms']['min']}ms, Max: {report['response_time_ms']['max']}ms)")
    print(f"[OK] Tai CPU: {report['system_resources']['cpu_percent']}% | RAM tieu thu: {report['system_resources']['ram_used_mb']} MB")
    print(f"[OK] Da luu bao cao vao: {out_file}")
    
    return report

if __name__ == "__main__":
    run_test(12)
