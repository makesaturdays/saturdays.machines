
from flask import Flask
from flask_pymongo import PyMongo



app = Flask(__name__, static_folder='../build')


app.config.from_object('config')

# try:
# 	app.config.from_object('config.environment_dev')
# except ImportError:
# 	pass


# app.mongo = PyMongo(app)

from core.helpers.verify_headers import *
from core.helpers.access_control_origin import *


