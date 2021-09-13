import os

BASE_API_URL = os.getenv("BASE_API_URL", "api/v1")
DEBUG_MODE = os.getenv("DEBUG_MODE", "no") == "yes"
DEV_MODE = os.getenv("DEV_MODE", "no") == "yes"
TEST_MODE = os.getenv("TEST_MODE", "no") == "yes"
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "no") == "yes"
DATABASE_NAME = os.getenv("DATABASE_NAME", "cloud_services")
DEV_REDIS = os.getenv("DEV_REDIS", "no") == "yes"
REDIS_HOST = os.getenv("REDIS_HOST", default="localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", default=6379))
REDIS_DB = os.getenv("REDIS_DB", default="0")
REDIS_NAMESPACE = os.getenv("REDIS_NAMESPACE", default="cloud_services")
REDIS_EXPIRE = int(os.getenv("REDIS_EXPIRE", default=60 * 60 * 24))
CRAZY_PRINTER_MODE = os.getenv("CRAZY_PRINTER_MODE", "no") == "yes"
TZ = os.getenv("TZ", "UTC")
