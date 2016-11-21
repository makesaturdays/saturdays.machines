
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from core import app
from core.helpers.json import to_json


from flask import request, abort
import os


from core.models.core.upload import Upload
Upload.define_routes()


from core.models.auth.token import Token
from core.models.auth.session import Session
from core.models.auth.user import User

Token.define_routes()
Session.define_routes()
User.define_routes()


import socket

@app.route('/details')
def details():
	# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# s.connect(('8.8.8.8', 0))

	return to_json({
		# 'ip_address': s.getsockname()[0]
	})



if __name__ == '__main__':
	if app.config['DEBUG']:
		app.run(threaded=True)

	else:
		http_server = HTTPServer(WSGIContainer(app))
		http_server.listen(5000)
		IOLoop.instance().start()

