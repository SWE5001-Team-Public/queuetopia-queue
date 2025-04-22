import asyncio
import time
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db, insert_static
from routes import config, reservation

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Initialize the database at startup."""
  await init_db()
  await insert_static()
  yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

router = APIRouter(prefix="/reservation-mgr")


# Health check endpoint
@router.get("/health", tags=["System"])
async def health_check():
  """Health check endpoint for monitoring service status."""
  return {"status": "healthy"}


@router.post("/load-test", tags=["System"])
async def load_test(
  cpu_load: int = Query(default=70, ge=10, le=99, description="CPU load percentage (10-99)"),
  duration: int = Query(default=5, ge=1, le=60, description="Duration in seconds (1-60)"),
  memory_mb: int = Query(default=100, ge=10, le=1000, description="Memory to allocate in MB (10-1000)")
):
  """
  Load testing endpoint that simulates heavy resource usage.
  E.g.: https://queuetopia.com/reservation-mgr/load-test?cpu_load=80&duration=30&memory_mb=500

  Parameters:
  - cpu_load: CPU load percentage to simulate (10-99%)
  - duration: Duration in seconds for the load test (1-60 seconds)
  - memory_mb: Memory to allocate in MB during the test (10-1000 MB)

  Returns metrics about the load test operation.
  """
  start_time = time.time()

  # Allocate memory
  memory_data = bytearray(memory_mb * 1024 * 1024)

  # CPU load simulation
  end_time = start_time + duration
  while time.time() < end_time:
    # Calculate load level
    target_usage = cpu_load / 100.0

    # Do CPU-intensive work (prime number calculation)
    cpu_start = time.time()
    find_primes(10000)  # Find primes up to 10000
    cpu_work_time = time.time() - cpu_start

    # Sleep to achieve target CPU usage
    sleep_time = cpu_work_time * (1 - target_usage) / target_usage
    if sleep_time > 0:
      await asyncio.sleep(sleep_time)

  # Clean up allocated memory
  del memory_data

  # Gather metrics
  total_time = time.time() - start_time

  return {
    "status": "completed",
    "requested_cpu_load": f"{cpu_load}%",
    "requested_memory": f"{memory_mb} MB",
    "requested_duration": f"{duration} seconds",
    "actual_duration": f"{total_time:.2f} seconds"
  }


def find_primes(limit):
  """Find all prime numbers up to the given limit using the Sieve of Eratosthenes."""
  sieve = [True] * (limit + 1)
  sieve[0] = sieve[1] = False

  for i in range(2, int(limit ** 0.5) + 1):
    if sieve[i]:
      for j in range(i * i, limit + 1, i):
        sieve[j] = False

  return [i for i in range(limit + 1) if sieve[i]]


# Other routes
router.include_router(config.router, prefix="/config", tags=["Config"])
router.include_router(reservation.router, prefix="/reservation", tags=["Reservation"])

app.include_router(router)

if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=5015)
