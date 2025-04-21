import uvicorn

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
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


# Other routes
router.include_router(config.router, prefix="/config", tags=["Config"])
router.include_router(reservation.router, prefix="/reservation", tags=["Reservation"])

app.include_router(router)

if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=5015)
