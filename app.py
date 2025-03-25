import uvicorn

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from routes import account, auth

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Initialize the database at startup."""
  await init_db()
  yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
  """Health check endpoint for monitoring service status."""
  return {"status": "healthy"}


# Other routes
app.include_router(auth.router, tags=["Authentication"])
app.include_router(account.router, prefix="/account", tags=["Account"])

if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=5000)
