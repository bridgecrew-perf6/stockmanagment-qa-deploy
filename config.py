import os
from datetime import timedelta

class Config(object):
    SECRET_KEY= os.environ.get('SECRET')
    # SQLALCHEMY_DATABASE_URI= 'sqlite:///teststockdb.sqlite3'
    SQLALCHEMY_DATABASE_URI= os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False