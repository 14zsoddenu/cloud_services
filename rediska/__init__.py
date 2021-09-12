from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_NAMESPACE, REDIS_EXPIRE, DEV_REDIS, TEST_MODE
from rediska.redict import Redict

if not TEST_MODE or DEV_REDIS:
    redis_db = Redict(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, namespace=REDIS_NAMESPACE, expire=REDIS_EXPIRE)
else:
    redis_db = {}
