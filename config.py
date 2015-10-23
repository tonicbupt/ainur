import os
import logging
import tempfile

SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
ERU_URL = os.getenv('ERU_URL', None)
DEBUG = int(os.getenv('DEBUG', 0))
PERMDIR = os.getenv('ERU_PERMDIR', tempfile.gettempdir())
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN', None)

LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'info').upper())
LOG_FILE = os.getenv('LOG_FILE', '')
LOG_FORMAT = os.getenv('LOG_FORMAT', '%(levelname)s:%(asctime)s:%(message)s')

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
