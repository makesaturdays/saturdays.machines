
from flask import Flask
from flask.ext.pymongo import PyMongo

# from celery import Celery



app = Flask(__name__, static_folder='build')


app.config.from_object('config.environment_default')

try:
	app.config.from_object('config.environment_dev')
except ImportError:
	pass

# app.config.from_object('config.schedule')


app.mongo = PyMongo(app)
app.caches = {}


# app.celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
# app.celery.config_from_object(app.config)


from core.helpers.verify_headers import *
from core.helpers.access_control_origin import *
from core.helpers.pages import *
from core.helpers.filters import *


