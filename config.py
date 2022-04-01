import os
from datetime import timedelta
from application import app

app.config['SQLALCHEMY_DATABASE_URI'] =os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] =os.environ.get('SECRET')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# class Config(object):
#     SECRET_KEY= os.environ.get('SECRET')
#     # SQLALCHEMY_DATABASE_URI= 'sqlite:///teststockdb.sqlite3'
#     SQLALCHEMY_DATABASE_URI= os.environ.get('DATABASE_URL')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False