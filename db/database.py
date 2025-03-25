import ssl
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")
print(f"🚀 Running in {ENVIRONMENT.upper()} environment")

if ENVIRONMENT == "prod":
  load_dotenv(".env.production")
elif ENVIRONMENT == "local":
  load_dotenv(".env.local")
else:
  load_dotenv(".env")  # Fallback to a default `.env` file

DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure DATABASE_URL is set
if not DATABASE_URL:
  raise ValueError("DATABASE_URL is not set. Check your .env file.")

# Configure SSL context for production database (only if needed)
ssl_context = ssl.create_default_context() if ENVIRONMENT == "prod" else None

# Create async engine
engine = create_async_engine(
  DATABASE_URL,
  echo=True,
  connect_args={"ssl": ssl_context} if ssl_context else {}
)

SessionLocal = sessionmaker(
  autocommit=False,
  autoflush=False,
  class_=AsyncSession,
  expire_on_commit=False
)

# Base model class
Base = declarative_base()


# Function to create tables asynchronously
async def create_tables():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


# Run table creation when the application starts
async def init_db():
  await create_tables()


# Dependency for async DB session
async def get_db():
  async with SessionLocal(bind=engine) as session:
    yield session
