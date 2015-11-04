import logging
import json
from redis import StrictRedis
from flask.ext.redis import FlaskRedis
from redis.exceptions import RedisError


class DecodedRedis(StrictRedis):
    @classmethod
    def from_url(cls, url, db=None, **kwargs):
        kwargs['decode_responses'] = True
        return StrictRedis.from_url(url, db, **kwargs)

rds = FlaskRedis.from_custom_provider(DecodedRedis)


def _safe_rds(default_ret=None):
    def wrapper(f):
        def g(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except (IOError, RedisError) as e:
                logging.exception(e)
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


@_safe_rds()
def safe_rds_hgetall(key):
    return rds.hgetall(key)
