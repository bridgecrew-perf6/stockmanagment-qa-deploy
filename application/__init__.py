# import the Flask class
from flask import Flask
from flask_sqlalchemy import  SQLAlchemy

#instatiate the Flask class and pass a special variable name 
app=Flask(__name__)

# import your config file
app.config.from_object("config.Config")

# instatiate SQLAlchemy and pass the app
db=SQLAlchemy(app)

# import all the apps routes 
from application import routes
from application import  models

# create all tables in db
db.create_all()
db.session.commit()