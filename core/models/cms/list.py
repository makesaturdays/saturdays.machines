from core import app
from flask import request, abort

from core.models.core.model import Model
from core.models.core.with_templates import WithTemplates
from core.models.core.has_routes import HasRoutes

from core.helpers.validation_rules import validation_rules
from core.helpers.json import to_json

from core.models.cms.author import Author

from bson.objectid import ObjectId
import markdown


with app.app_context():
	class List(WithTemplates, HasRoutes, Model):

		collection_name = 'lists'

		schema = {
			'title': validation_rules['text'],
			'route': validation_rules['text'],
			'thumbnail': validation_rules['image'],
			'image': validation_rules['image'],
			# 'template': {
			# 	'type': 'dict',
			# 	'schema': {
			# 		'thumbnail': validation_rules['image'],
			# 		'image': validation_rules['image'],
			# 		'content': validation_rules['content'],
			# 		'tags': validation_rules['text_list'],
			# 		'metadata': validation_rules['metadata']
			# 	}
			# },
			'is_online': validation_rules['bool'],
			'metadata': validation_rules['metadata']
		}

		endpoint = '/lists'
		routes = [
			{
				'route': '',
				'view_function': 'list_view',
				'methods': ['GET']
			},
			{
				'route': '',
				'view_function': 'create_view',
				'methods': ['POST'],
				'requires_admin': True
			},
			{
				'route': '/<string:_id>',
				'view_function': 'get_view',
				'methods': ['GET']
			},
			{
				'route': '/<ObjectId:_id>',
				'view_function': 'update_view',
				'methods': ['PATCH', 'PUT'],
				'requires_admin': True
			},
			{
				'route': '/<ObjectId:_id>',
				'view_function': 'delete_view',
				'methods': ['DELETE'],
				'requires_admin': True
			},
			{
				'route': '/<string:_id>/tags/<string:tag>',
				'view_function': 'tags_get_view',
				'methods': ['GET']
			},
			{
				'route': '/<string:_id>/authors/<string:handle>',
				'view_function': 'authors_get_view',
				'methods': ['GET']
			}
		]


		templates = [
			{
				'view_function': 'list_view',
				'template': 'lists/lists.html',
				'response_key': 'lists',
				'prerender_process': '_list_values'
			},
			{
				'view_function': 'get_view',
				'template': 'lists/<route>.list.html',
				'response_key': 'list',
				'prerender_process': '_prerender'
			},
			{
				'view_function': 'tags_get_view',
				'template': 'lists/<route>.list.html',
				'response_key': 'list',
				'prerender_process': '_prerender'
			},
			{
				'view_function': 'authors_get_view',
				'template': 'lists/<route>.list.html',
				'response_key': 'list',
				'prerender_process': '_prerender'
			}
		]


		@classmethod
		def update(cls, _id, document, other_operators={}, projection={}):

			# try:
			# 	for key in document['template']['content'].copy().keys():
			# 		document['template.content.'+key] = document['template']['content'].pop(key)

			# 	del document['template']['content']
			# except KeyError:
			# 	pass

			# try:
			# 	for key in document['template'].copy().keys():
			# 		document['template.'+key] = document['template'].pop(key)

			# 	del document['template']

			# except KeyError:
			# 	pass

			return super().update(_id, document, other_operators, projection)



		@classmethod
		def postprocess(cls, document):
			tag_counts = {}
			document['tags'] = []
			document['highest_tag_count'] = 0

			try:
				posts = []
				for post in document['posts']:
					if request.current_session_is_admin:
						posts.append(post)

					elif post['is_online']:
						posts.append(post)
				document['posts'] = posts


				for post in document['posts']:
					try:
						for tag in post['tags']:
							if tag in tag_counts:
								tag_counts[tag] += 1
							else:
								tag_counts[tag] = 1

					except KeyError:
						pass
						

				for (key, value) in tag_counts.items():
					document['tags'].append({'name':key, 'count':value})
					if value > document['highest_tag_count']:
						document['highest_tag_count'] = value

			except KeyError:
				pass



			return document



		@classmethod
		def tags_get_view(cls, _id, tag):
			document = cls.get(_id)

			try:
				posts = []
				for post in document['posts']:
					try:
						if tag in post['tags']:
							posts.append(post)
					except KeyError:
						pass

				document['posts'] = posts

			except KeyError:
				pass


			return cls._format_response(document)



		@classmethod
		def authors_get_view(cls, _id, handle):
			document = cls.get(_id)
			author = Author.get(handle)

			try:
				posts = []
				for post in document['posts']:
					try:
						if author['_id'] in post['authors']:
							posts.append(post)
					except KeyError:
						pass

				document['posts'] = posts

			except KeyError:
				pass


			return cls._format_response(document)





		# HELPERS
		@classmethod
		def _values(cls):
			
			documents = {}
			for document in cls.list():
				documents[document['route']] = cls._prerender(document)

			return documents


		@classmethod
		def _prerender(cls, response):
			
			authors = Author.list()
			response['authors'] = authors

			try:
				posts = []

				for post in response['posts']:
					try:
						post_authors = []

						for post_author in post['authors']:
							for author in authors:
								if author['_id'] == post_author:
									post_authors.append(author)
									break

						post['author_ids'] = post['authors']
						post['authors'] = post_authors

					except KeyError:
						pass



				for post in response['posts']:
					post_values = post.copy()

					try:
						for (key, value) in post_values['content'].items():
							if 'is_markdown' in value and value['is_markdown']:
								post_values[key] = markdown.markdown(value['value'])
							else:
								post_values[key] = value['value']
						del post_values['content']

					except KeyError:
						pass

					posts.append(post_values)

				def get_published_at(post):
					return post['published_at']

				response['posts'] = sorted(posts, key=get_published_at)
				response['posts'].reverse()

			except KeyError:
				pass
				

			return response






