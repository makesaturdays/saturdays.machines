from core import app
from flask import request, abort
from werkzeug.exceptions import NotFound

from core.models.core.model import Model
from core.models.core.has_routes import HasRoutes

from core.models.auth.token import Token
from core.models.auth.user import User

from core.helpers.validation_rules import validation_rules
from core.helpers.raise_error import raise_error

from bson.objectid import ObjectId

import hashlib
import uuid
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone


with app.app_context():
	class Session(HasRoutes, Model):

		collection_name = 'sessions'

		schema = {
			'token_code': validation_rules['text'],
			'email': validation_rules['email'],
			'password': validation_rules['password'],
		}



		endpoint = '/sessions'
		routes = [
			{
				'route': '',
				'view_function': 'create_view',
				'methods': ['POST']
			},
			{
				'route': '/<ObjectId:_id>',
				'view_function': 'get_view',
				'methods': ['GET'],
				'requires_session': True
			},
			{
				'route': '/<ObjectId:_id>',
				'view_function': 'update_view',
				'methods': ['PATCH', 'PUT'],
				'requires_session': True
			},
			{
				'route': '/<ObjectId:_id>',
				'view_function': 'delete_view',
				'methods': ['DELETE'],
				'requires_session': True
			}
		]


		@classmethod
		def create(cls, document):

			if 'token_code' in document:
				try:
					token = Token.get_where({'code': document['token_code']})
					if datetime.now(timezone(app.config['TIMEZONE'])) > token['created_at'] + relativedelta(days=+1):
						raise_error('auth', 'token_expired', 403)

					document['token_id'] = token['_id']
					document['user_id'] = token['user_id']
					request.user_id = document['user_id']
					
					try:
						document['is_admin'] = token['is_admin']
					except KeyError:
						pass

					del document['token_code']

				except NotFound:
					raise_error('auth', 'token_not_found', 404)


			secret = uuid.uuid4().hex
			document['secret_hash_salt'] = uuid.uuid4().hex
			document['secret_hash'] = hashlib.sha256(secret.encode('utf-8') + document['secret_hash_salt'].encode('utf-8')).hexdigest()

			document['_id'] = ObjectId()
			document['session_id'] = document['_id']

			document = super().create(document)
			document['secret'] = secret

			try:
				document['user_id'] = request.user_id
			except AttributeError:
				pass

			return document
			

			



		@classmethod
		def preprocess(cls, document):
			try:
				if 'password' in document and document['password'] is not None:
					user = app.mongo.db[User.collection_name].find_one_or_404({
						'email': document['email']
					})

					if user['password'] != hashlib.sha256(document['password'].encode('utf-8') + user['password_salt'].encode('utf-8')).hexdigest():
						raise_error('auth', 'password_incorrect', 403)

					document['user_id'] = user['_id']
					request.user_id = document['user_id']

					try:
						document['is_admin'] = user['is_admin']
					except KeyError:
						pass

					del document['email']
					del document['password']

				else:
					document['user_id'] = User.create({'email': document['email']})['_id']
					request.user_id = document['user_id']
					del document['email']

				
			except KeyError:
				pass


			return super().preprocess(document)



		@classmethod
		def postprocess(cls, document):
			try:
				del document['secret_hash']
				del document['secret_hash_salt']
				
			except KeyError:
				pass


			if 'is_admin' not in document:
				document['is_admin'] = False


			return document

	



