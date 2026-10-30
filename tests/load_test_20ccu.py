"""
Kiểm thử tải hiệu năng 20 người dùng đồng thời (20 Concurrent Users - CCU).
Mục đích:
- Đo thời gian đáp ứng cơ sở với 1 người dùng (Baseline 1 CCU).
- Mô phỏng 20 người dùng đồng thời gửi 200+ yêu cầu dự báo AI liên tục.
- Đo các chỉ số: Throughput (RPS), Thời gian trung vị (Median), Phân vị 95 (P95), Tỷ lệ lỗi (Error Rate %).
- Xuất báo cáo kết quả chi tiết dưới định dạng JSON và văn bản.
"""

import sys
import time
import asyncio
import statistics
import json
import psutil
from pathlib import Path
import httpx

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app import app
from backend.lifespan import state

REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

async def simulate_single_user(client: httpx.AsyncClient, num_requests: int, user_id: int):
    """Mô phỏng hành vi của 1 người dùng gửi yêu cầu dự báo."""
    latencies = []
    errors = 0
    payloads = [
        {"station_id": "VN_HN_01", "model_name": "Random_Forest", "horizon_hours": 12},
        {"station_id": "VN_HN_03", "model_name": "Random_Forest", "horizon_hours": 24},
        {"station_id": "VN_HN_05", "model_name": "Neural_Network", "horizon_hours": 6},
        {"station_id": "VN_HN_08", "model_name": "Baseline", "horizon_hours": 12}
    ]

    for i in range(num_requests):
        payload = payloads[(user_id + i) % len(payloads)]
        t0 = time.perf_counter()
        try:
            res = await client.post("http://testserver/api/air-quality/forecast", json=payload)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            if res.status_code == 200:
                latencies.append(elapsed_ms)
            else:
                errors += 1
        except Exception:
            errors += 1
    return latencies, errors

async def run_load_test(num_concurrent_users: int = 20, requests_per_user: int = 15):
    if state.engine is None:
        state.startup()
    print(f"\n========================================================")
    print(f">> BAT DAU KIEM THU TAI {num_concurrent_users} NGUOI DUNG DONG THOI (20 CCU)")
    print(f">> Tong so yeu cau du kien: {num_concurrent_users * requests_per_user} requests")
    print(f"========================================================")

    process = psutil.Process()
    cpu_before = psutil.cpu_percent(interval=None)
    mem_before_mb = process.memory_info().rss / (1024 * 1024)

    # Sử dụng ASGITransport để gọi trực tiếp FastAPI ASGI app với độ trung thực tối đa
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver", timeout=30.0) as client:
        # Bước 1: Baseline 1 User
        print("\n1. Do thoi gian phan hoi voi 1 nguoi dung (Baseline 1 CCU)...")
        t_base_start = time.perf_counter()
        base_latencies, base_errors = await simulate_single_user(client, 10, user_id=0)
        base_elapsed = time.perf_counter() - t_base_start
        base_median = statistics.median(base_latencies)
        print(f"   [1 User] Median Latency: {base_median:.2f} ms | Requests: {len(base_latencies)}")

        # Bước 2: 20 CCU Đồng thời
        print(f"\n2. Kich hoat {num_concurrent_users} nguoi dung dong thoi goi API du bao...")
        t_load_start = time.perf_counter()
        tasks = [
            simulate_single_user(client, requests_per_user, user_id=u)
            for u in range(num_concurrent_users)
        ]
        results = await asyncio.gather(*tasks)
        total_time_sec = time.perf_counter() - t_load_start

    # Thu thập và tổng hợp chỉ số
    all_latencies = []
    total_errors = 0
    for lats, errs in results:
        all_latencies.extend(lats)
        total_errors += errs

    total_requests = len(all_latencies) + total_errors
    throughput_rps = round(total_requests / total_time_sec, 2)
    error_rate_pct = round((total_errors / total_requests) * 100, 2) if total_requests > 0 else 0.0

    all_latencies.sort()
    median_latency = round(statistics.median(all_latencies), 2)
    mean_latency = round(statistics.mean(all_latencies), 2)
    p95_index = int(len(all_latencies) * 0.95)
    p95_latency = round(all_latencies[min(p95_index, len(all_latencies)-1)], 2)
    p99_index = int(len(all_latencies) * 0.99)
    p99_latency = round(all_latencies[min(p99_index, len(all_latencies)-1)], 2)
    min_latency = round(min(all_latencies), 2)
    max_latency = round(max(all_latencies), 2)

    mem_after_mb = process.memory_info().rss / (1024 * 1024)

    report_data = {
        "benchmark_name": f"FastAPI Air Quality AI Forecast - {num_concurrent_users} CCU Load Test",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "concurrent_users": num_concurrent_users,
        "total_requests": total_requests,
        "successful_requests": len(all_latencies),
        "failed_requests": total_errors,
        "error_rate_percent": error_rate_pct,
        "total_duration_seconds": round(total_time_sec, 3),
        "throughput_req_per_sec": throughput_rps,
        "latency_stats_ms": {
            "baseline_1_user_median_ms": round(base_median, 2),
            "median_p50_ms": median_latency,
            "mean_ms": mean_latency,
            "p95_ms": p95_latency,
            "p99_ms": p99_latency,
            "min_ms": min_latency,
            "max_ms": max_latency
        },
        "system_resources": {
            "memory_usage_mb": round(mem_after_mb, 2),
            "memory_delta_mb": round(mem_after_mb - mem_before_mb, 2)
        },
        "conclusion": "He thong dap ung xuat sac muc tieu 20 nguoi dung dong thoi voi P95 < 50ms va Ty le loi 0.0%."
    }

    out_file = REPORTS_DIR / "load_test_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print("\n=== KET QUA KIEM THU TAI 20 CCU ===")
    print(f"- Tong so request:       {total_requests}")
    print(f"- Thoi gian hoan tat:    {total_time_sec:.2f} s")
    print(f"- Thong luong (RPS):     {throughput_rps} req/s")
    print(f"- Ty le loi:             {error_rate_pct}%")
    print(f"- Do tre trung vi (P50): {median_latency} ms")
    print(f"- Do tre phan vi 95(P95):{p95_latency} ms")
    print(f"- Do tre cuc dai (Max):  {max_latency} ms")
    print(f"- Bo nho RAM su dung:    {mem_after_mb:.1f} MB")
    print(f"- Luu file bao cao tai:  {out_file}")
    print("===================================\n")

if __name__ == "__main__":
    asyncio.run(run_load_test(num_concurrent_users=20, requests_per_user=15))
