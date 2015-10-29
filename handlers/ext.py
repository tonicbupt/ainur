import json
from flask.ext.redis import FlaskRedis
from redis.exceptions import RedisError

rds = FlaskRedis()


def _safe_rds(default_ret=None):
    def wrapper(f):
        def g(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except (IOError, RedisError):
                return default_ret
        return g
    return wrapper


@_safe_rds()
def safe_rds_get(key):
    val = rds.get(key)
    return None if val is None else json.loads(val)


@_safe_rds()
def safe_rds_set(key, val):
    rds.set(key, json.dumps(val))
