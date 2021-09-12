from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_NAMESPACE, REDIS_EXPIRE
from rediska.redict import Redict

redis_db = Redict(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, namespace=REDIS_NAMESPACE, expire=REDIS_EXPIRE)
