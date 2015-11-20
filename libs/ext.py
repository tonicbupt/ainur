# coding: utf-8

from redis import StrictRedis
from flask.ext.redis import FlaskRedis
from flask.ext.sqlalchemy import SQLAlchemy


class DecodedRedis(StrictRedis):

    @classmethod
    def from_url(cls, url, db=None, **kwargs):
        kwargs['decode_responses'] = True
        return StrictRedis.from_url(url, db, **kwargs)


rds = FlaskRedis.from_custom_provider(DecodedRedis)
db = SQLAlchemy()
