import asyncio

import random

import statistics

import time

from dataclasses import dataclass

from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"

FILES = [
    "src/tests/fixtures/01_rapport_incident_biomethane.docx",
    "src/tests/fixtures/02_avenant_convention_injection.docx",
    "src/tests/fixtures/03_manuel_compresseur_edge_cases.docx",
]


STAGES = [
    (5, 30),  # 5 concurrent requests for 30 seconds
    (10, 30),  # 10 concurrent requests for 30 seconds
    (25, 45),  # 20 concurrent requests for 45 seconds
    (50, 45),  # 50 concurrent requests for 45 seconds
]

@dataclass
class RequestResult:
    endpoint: str
    status_code: int
    duration: float
    error: str | None = None

results: list[RequestResult] = []


async def request(
        client: httpx.AsyncClient,
        method: str,
        url: str,
        endpoint: str,
        **kwargs
):
    started = time.perf_counter()
    try:
        response = await client.request(method, url, **kwargs)
        duration = time.perf_counter() - started
        results.append(RequestResult(endpoint=endpoint, status_code=response.status_code, duration=duration))
    except Exception as e:
        duration = time.perf_counter() - started
        results.append(RequestResult(endpoint=endpoint, status_code=0, duration=duration, error=str(e)))


async def health(client: httpx.AsyncClient):
    return await request(client, "GET", f"{BASE_URL}/health", endpoint="health")

async def list_jobs(client: httpx.AsyncClient):
    return await request(client, "GET", f"{BASE_URL}/api/v1/jobs/", endpoint="list_jobs")


async def not_found(client: httpx.AsyncClient):
    return await request(client, "GET", f"{BASE_URL}/api/v1/jobs/999999", endpoint="not_found")

async def upload_file(client: httpx.AsyncClient):
    filename = random.choice(FILES)
    with open(filename, "rb") as f:
        await request(client, "POST", f"{BASE_URL}/api/v1/ingestion/documents/", endpoint="upload_file", files={"file": (Path(filename).name, f)})

async def perform_requests(client: httpx.AsyncClient, duration: int):
    end_time = time.time() + duration
    while time.time() < end_time:
        choice = random.choices(
            [health, list_jobs, not_found, upload_file],
            weights=[50, 30, 15, 5]
        )[0]
        await choice(client)

async def worker(client: httpx.AsyncClient, stop_event: asyncio.Event):
    while not stop_event.is_set():
        await perform_requests(client, duration=1)

        await asyncio.sleep(
            random.uniform(0.1, 0.5)
        )  # Wait for a random time between 0.1 and 0.5 seconds between requests

async def run_load_test(num_workers: int, duration: int):
    print()
    print("=" * 50)
    print(f"STAGE: {num_workers} concurrent requests for {duration} seconds")
    print("=" * 50)
    stop_event = asyncio.Event()
    limits = httpx.Limits(max_connections=num_workers, max_keepalive_connections=num_workers)
    timeout = httpx.Timeout(
        connect=5, read=30, write=30, pool=30
    )
    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        tasks = [asyncio.create_task(worker(client, stop_event)) for _ in range(num_workers)]
        await asyncio.sleep(duration)
        stop_event.set()
        await asyncio.gather(*tasks, return_exceptions=True)

def percentile(data: list[float], percentile: float) -> float:
    size = len(data)
    if size == 0:
        return 0.0
    sorted_data = sorted(data)
    index = int(size * percentile / 100)
    return sorted_data[min(index, size - 1)]

def print_reports(
        total_duration: float,
):
    print()
    print("=" * 50)
    print("LOAD TEST REPORT")
    print("=" * 50)
    print(f"Total duration: {total_duration:.2f} seconds")
    print(f"Total requests: {len(results)}")
    successful_requests = [r for r in results if r.status_code == 200]
    failed_requests = [r for r in results if r.status_code != 200]
    print(f"Successful requests: {len(successful_requests)}")
    print(f"Failed requests: {len(failed_requests)}")
    if successful_requests:
        durations = [r.duration for r in successful_requests]
        print(f"Average response time: {statistics.mean(durations):.2f} seconds")
        print(f"Median response time: {statistics.median(durations):.2f} seconds")
        print(f"95th percentile response time: {percentile(durations, 95):.2f} seconds")
        print(f"99th percentile response time: {percentile(durations, 99):.2f} seconds")

async def main():
    print("Starting load test...")
    print(f"Target URL: {BASE_URL}")
    for file in FILES:
        print(f"Using file: {file}")
    start_time = time.perf_counter()
    for num_workers, duration in STAGES:
        await run_load_test(num_workers, duration)

        await asyncio.sleep(10)  # Wait for 10 seconds between stages
    total_duration = time.perf_counter() - start_time
    print_reports(total_duration)

if __name__ == "__main__":
    asyncio.run(main())