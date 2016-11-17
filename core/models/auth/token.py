from core import app
from flask import request, abort
from werkzeug.exceptions import NotFound

from core.models.core.model import Model
from core.models.core.has_routes import HasRoutes

from core.helpers.validation_rules import validation_rules
from core.helpers.raise_error import raise_error

from core.models.auth.user import User

import string
import random
import uuid


with app.app_context():
	class Token(HasRoutes, Model):

		collection_name = 'tokens'

		schema = {
			'email': validation_rules['email']
		}


		endpoint = '/tokens'
		routes = [
			{
				'route': '',
				'view_function': 'list_view',
				'methods': ['GET'],
				'requires_admin': True
			},
			{
				'route': '',
				'view_function': 'create_view',
				'methods': ['POST']
			},
			{
				'route': '/<ObjectId:_id>',
				'view_function': 'get_view',
				'methods': ['GET'],
				'requires_admin': True
			},
			{
				'route': '/<ObjectId:_id>',
				'view_function': 'delete_view',
				'methods': ['DELETE'],
				'requires_admin': True
			}
		]


		@classmethod
		def create(cls, document):

			try:
				user = User.get_where({
					'email': document['email']
				})
			except NotFound:
				raise_error('auth', 'user_not_found', 404)

			document['code'] = uuid.uuid4().hex
			document['user_id'] = user['_id']

			try:
				document['is_admin'] = user['is_admin']
			except KeyError:
				pass


			return super().create(document)


	



