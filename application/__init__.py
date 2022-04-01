# import the Flask class
import os
from flask import Flask
from flask_sqlalchemy import  SQLAlchemy

#instatiate the Flask class and pass a special variable name 
app=Flask(__name__)

# import your config file
# app.config.from_object("config.Config")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://jkktzcsikaxquq:0372341fb2bc6d87f2f6ea288b655d7ff521bd9b772a5b2d04d3662b3fb21e76@ec2-3-229-161-70.compute-1.amazonaws.com:5432/d4f8s3lohg5na0'
app.config['SECRET_KEY'] = 'Ol8sSHeqgWsv5_WueuC4og'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# instatiate SQLAlchemy and pass the app
db=SQLAlchemy(app)

# import all the apps routes 
from application import routes
from application import  models

# create all tables in db
db.create_all()
db.session.commit()