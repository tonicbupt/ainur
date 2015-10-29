import os
import json
import logging
import calendar
import urllib2
import flask
import werkzeug.exceptions

from cgi import parse_qs
from eruhttp import EruException
from datetime import datetime
from functools import wraps
from flask import request, Response
from urlparse import urlparse

from config import GITLAB_DOMAIN


def paginator_kwargs(kw):
    d = kw.copy()
    d.pop('start', None)
    d.pop('limit', None)
    return d


def urlencode(text):
    return urllib2.quote(text.encode('utf8'), safe='')


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


def strip_irregular_space(s):
    return s.replace('\t', '').replace('\r', '')


def post_body():
    return request.environ['body_copy']


def post_body_text():
    return unicode(strip_irregular_space(post_body()), 'utf-8')


def post_json():
    return json.loads(post_body_text())


def post_form():
    try:
        return {k: unicode(strip_irregular_space(v[0]), 'utf-8')
                for k, v in parse_qs(post_body()).iteritems()}
    except (ValueError, TypeError, AttributeError, LookupError):
        return {}


def forbid(self):
    raise werkzeug.exceptions.Forbidden()


def send_file(filename, mimetype=None):
    return flask.send_file(filename, mimetype=mimetype, conditional=True)


def send_template(module, templ):
    if '..' in templ or '/' == templ[0]:
        return not_found()
    try:
        return flask.send_file(os.path.join('templates', module, templ),
                               'text/html')
    except IOError:
        return not_found()


def not_found():
    return flask.abort(404)


def json_api(f):
    @wraps(f)
    def g(*args, **kwargs):
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
    return g


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
