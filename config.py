import logging
import os

from dotenv import load_dotenv


def load_environment():
  env = os.getenv("ENVIRONMENT", "prod")
  if env == "prod":
    load_dotenv(".env.production")
  elif env == "local":
    load_dotenv(".env.local")
  else:
    load_dotenv(".env")


def setup_logging():
  log_level_str = os.environ.get("LOGGING_LEVEL", "INFO").upper()
  numeric_level = getattr(logging, log_level_str, logging.INFO)

  logging.basicConfig(
    level=numeric_level,
    format=r'%(asctime)s|%(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
  )
