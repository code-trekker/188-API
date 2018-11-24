from flask import Flask, Blueprint, request, abort,url_for, jsonify, g, render_template, make_response,session
from flask_sqlalchemy import SQLAlchemy
import os, sqlalchemy, datetime, jwt
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_cors import CORS, cross_origin
from datetime import date, timedelta
from dateutil import parser
import time, pytz

app = Flask(__name__)

cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1234@localhost/wma'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['USE_SESSION_FOR_NEXT'] = True
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'thisissecret'
app.secret_key = os.urandom(24)

db = SQLAlchemy(app)

import wmapp.api

def createDB():
    engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:1234@localhost') #connects to server
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("create database wma")
    conn.close()

def createTables():
    db.create_all()

# createDB()
createTables()