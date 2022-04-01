import os
from datetime import timedelta

class Config(object):
    SECRET_KEY= os.environ.get('SECRET_KEY') or "secrete_string"
    # SQLALCHEMY_DATABASE_URI= 'sqlite:///teststockdb.sqlite3'
    SQLALCHEMY_DATABASE_URI= 'postgres://imwosyeftskruk:f9665cf0ad6ae9db056912da7a7de00f6f5f4eac53b56e12da8853b1770d6f6d@ec2-52-3-60-53.compute-1.amazonaws.com:5432/dchfk1gftccen9'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=10)