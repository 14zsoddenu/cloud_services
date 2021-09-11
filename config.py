import os

BASE_API_URL = os.getenv("BASE_API_URL", "api/v1")
DEBUG_MODE = os.getenv("DEBUG_MODE", "no") == "yes"
TEST_MODE = os.getenv("TEST_MODE", "no") == "yes"
