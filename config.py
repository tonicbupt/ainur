import os
import logging
import tempfile

DEBUG = int(os.getenv('DEBUG', 0))
SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
SECRET = os.getenv('SECRET', 'ainur')

MAX_CONTENT_LENGTH = 16 * 1024 * 1024

ERU_URL = os.getenv('ERU_URL', None)
PERMDIR = os.getenv('ERU_PERMDIR', tempfile.gettempdir())
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN', None)
GITLAB_DOMAIN = os.getenv('GITLAB_DOMAIN', 'git.hunantv.com')

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'ainur')

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'info').upper())
LOG_FILE = os.getenv('LOG_FILE', '')
LOG_FORMAT = os.getenv('LOG_FORMAT', '%(levelname)s:%(asctime)s:%(message)s')

SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', '100'))
SQLALCHEMY_POOL_TIMEOUT = int(os.getenv('SQLALCHEMY_POOL_TIMEOUT', '3600'))
SQLALCHEMY_POOL_RECYCLE = int(os.getenv('SQLALCHEMY_POOL_RECYCLE', '2000'))

APPNAME_ERU_LB = 'erulb'

OPENID_LOGIN_URL = 'http://openids-web.intra.hunantv.com/oauth/login?return_to=%s&url=%s'
OPENID_PROFILE_URL = 'http://openids-web.intra.hunantv.com/oauth/profile/'

try:
    from local_config import *
except ImportError:
    pass

if not ERU_URL:
    raise ValueError('ERU_URL is not set')


def init_logging():
    args = {'level': LOG_LEVEL}
    if LOG_FILE:
        args['filename'] = LOG_FILE
    args['format'] = LOG_FORMAT
    logging.basicConfig(**args)

init_logging()

SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%d/%s' % (
        MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE)
REDIS_URL = 'redis://%s:%d/0' % (REDIS_HOST, REDIS_PORT)
