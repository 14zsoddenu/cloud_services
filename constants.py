REDIS_CONTAINER_CONFIG = dict(
    image_name="redis:latest",
    ports={"6379/tcp": 6380},
    auto_remove=True,
)
PRECISE_DATETIME_STRING_TEMPLATE = "%Y-%m-%d %H:%M:%S.%f"
