
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from core import app
from core.helpers.json import to_json


from flask import request, abort
import os


# from core.models.core.upload import Upload
# Upload.define_routes()


# from core.models.auth.token import Token
# from core.models.auth.session import Session
# from core.models.auth.user import User

# Token.define_routes()
# Session.define_routes()
# User.define_routes()


@app.route('/details')
def details():

	return to_json({
		'version': '0.1'
	})


if __name__ == '__main__':
	app.run(threaded=True, port=80)
