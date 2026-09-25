import asyncio
import random
import time
import httpx

BASE_URL = "http://127.0.0.1:8000"

FILES = [
    "src/tests/fixtures/01_rapport_incident_biomethane.docx",
    "src/tests/fixtures/02_avenant_convention_injection.docx",
    "src/tests/fixtures/03_manuel_compresseur_edge_cases.docx",
]

async def health(client: httpx.AsyncClient):
    return await client.get(f"{BASE_URL}/health")

async def list_jobs(client: httpx.AsyncClient):
    return await client.get(f"{BASE_URL}/api/v1/jobs/")

async def not_found(client: httpx.AsyncClient):
    return await client.get(f"{BASE_URL}/api/v1/jobs/999999")

async def upload(client: httpx.AsyncClient):
    filename = random.choice(FILES)
    with open(filename, "rb") as f:
        files = {"file": (filename, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        return await client.post(f"{BASE_URL}/api/v1/ingestion/documents/", files=files, timeout=60.0)

async def execute_request(client: httpx.AsyncClient):
    choice = random.choices([health, list_jobs, not_found, upload], weights=[50, 30, 15, 5])[0]

    started = time.perf_counter()

    try:
        response = await choice(client)

        duration = time.perf_counter() - started
        print(f"Request to {choice.__name__} took {duration:.2f} seconds. Status code: {response.status_code}")
    except Exception as e:
        duration = time.perf_counter() - started
        print(f"Request to {choice.__name__} failed after {duration:.2f} seconds. Error: {e}")

async def main():
    async with httpx.AsyncClient() as client:
        for batch in range(20):  # 20 batches
            tasks = [execute_request(client) for _ in range(10)]  # 10 requests per batch
            await asyncio.gather(*tasks)
            await asyncio.sleep(
                random.uniform(0.1, 1.0)
            )  # Wait for a random time between 0.1 and 1.0 seconds between batches

if __name__ == "__main__":
    asyncio.run(main())