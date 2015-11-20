# coding: utf-8

import sys
import os

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path)

from handlers.app import create_app
from libs.ext import db, rds
from models import *

def flushdb(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        rds.flushall()

if __name__ == '__main__':
    app = create_app()
    if app.config['MYSQL_HOST'] in ('127.0.0.1', 'localhost') or '--force' in sys.argv:
        flushdb(app)
    else:
        print 'you are not doing this on your own computer,'
        print 'if sure, add --force to flush database.'
