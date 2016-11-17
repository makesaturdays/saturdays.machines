
from core import app
from core.helpers.json import to_json, json_formater

from flask import request, abort
from flask import render_template, json

from core.models.cms.piece import Piece
from core.models.cms.list import List

from werkzeug.contrib.cache import SimpleCache

import os



def page(lang=None):

	cached_template = app.caches['/pages'].get(request.path)
	if cached_template is None or app.config['DEBUG']:

		response = {
			'pieces': Piece._values(lang),
			'lists': List._values(),
			'root': request.host_url,
			'debugging': app.config['DEBUG']
		}
		response['pieces_json'] = json.dumps(response['pieces'], sort_keys=False, default=json_formater)

		if lang is None:
			response['lang_route'] = '/'

		else:
			response['lang'] = lang
			response['lang_route'] = '/' + lang + '/'


		render = render_template('pages/' + request.endpoint + '.html', **response)
		app.caches['/pages'].set(request.path, render, timeout=0)
		return render

	else:
		return cached_template


app.caches['/pages'] = SimpleCache()
for file in os.listdir(os.getcwd()+'/core/templates/pages'):
	

	if file == 'index.html':
		app.add_url_rule('/', 'index', methods=['GET'])
		app.view_functions['index'] = page

		for lang in app.config['LANGS']:
			app.add_url_rule('/' + lang + '/', 'index', methods=['GET'], defaults={'lang': lang})

	else:
		route = file.replace('.html', '')
		app.add_url_rule('/' + route, route, methods=['GET'])
		app.view_functions[route] = page

		for lang in app.config['LANGS']:
			app.add_url_rule('/' + lang + '/' + route, route, methods=['GET'], defaults={'lang': lang})

		




