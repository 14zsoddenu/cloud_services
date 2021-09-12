import json

from redis_dict import RedisDict


class Redict(RedisDict):
    trans = {
        "json": json.loads,
        type("").__name__: str,
        type(1).__name__: int,
        type(0.1).__name__: float,
        type(True).__name__: lambda x: x == "True",
        type(None).__name__: lambda x: None,
        type(dict()).__name__: lambda x: json.loads(x.replace("'", '"')),
    }
