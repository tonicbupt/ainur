# coding: utf-8

import json
import logging
import calendar
import urllib
import functools

from eruhttp import EruException
from datetime import datetime
from flask import Response, abort, g, request
from urlparse import urlparse

from config import GITLAB_DOMAIN, OPENID_LOGIN_URL
from models.base import Base


def paginator_kwargs(kw):
    d = kw.copy()
    d.pop('start', None)
    d.pop('limit', None)
    return d


def tojson(obj):
    def default(obj):
        if isinstance(obj, datetime):
            return long(1000 * calendar.timegm(obj.timetuple()))
        return obj
    return json.dumps(obj, default=default).replace(
        '<', u'\\u003c').replace('>', u'\\u003e').replace(
            '&', u'\\u0026').replace("'", u'\\u0027')


def json_result(obj, status_code=200):
    r = Response(tojson(obj), mimetype='application/json')
    r.status_code = status_code
    return r


def json_api(f):
    @functools.wraps(f)
    def _(*args, **kwargs):
        try:
            return json_result(f(*args, **kwargs)) or ''
        except KeyError, e:
            r = dict(reason='missing argument', missing=e.message)
        except UnicodeEncodeError, e:
            r = dict(reason='invalid input encoding')
        except ValueError, e:
            r = dict(reason=e.message)
        except EruException, e:
            logging.exception(e)
            r = dict(reason='eru fail', detail=e.message)
        except StandardError, e:
            logging.error('UNEXPECTED ERROR')
            logging.exception(e)
            return json_result(
                {'reason': 'unexpected', 'msg': e.message}, 500)
        return json_result(r, 400)
    return _


def parse_git_url(url):
    if url.startswith('http://' + GITLAB_DOMAIN):
        r = urlparse(url)
        r = r.path[1:]
        r = r[:-4] if r.endswith('.git') else r
        return r
    if url.startswith('git@' + GITLAB_DOMAIN):
        r = url.split(':')[1][:-4]
        return r

    raise ValueError('Invalid url for git repository')


def demand_login(f):
    @functools.wraps(f)
    def h(*args, **kwargs):
        if not g.user:
            abort(401)
        return f(*args, **kwargs)
    return h


def login_url():
    url = urllib.quote(request.host_url + 'user/login_from_openid/', safe='')
    return OPENID_LOGIN_URL % (url, request.host_url)


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Base):
            return obj.to_dict()
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(JSONEncoder, self).default(obj)


def jsonize(f):
    @functools.wraps(f)
    def _(*args, **kwargs):
        r = f(*args, **kwargs)
        code, data = r if isinstance(r, tuple) else (200, r)
        return Response(json.dumps(data, cls=JSONEncoder), status=code, mimetype='application/json')
    return _
