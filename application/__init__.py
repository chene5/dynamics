"""
The flask application package.
"""
from flask import Flask

from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

application = Flask(__name__)
application.config.from_object('config')

login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'signin'
login_manager.init_app(application)

db = SQLAlchemy(application)
from application import views, models
"""
from application import views
"""
