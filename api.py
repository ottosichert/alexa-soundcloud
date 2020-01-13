from copy import deepcopy
from datetime import datetime
import random
from urllib.parse import urlparse

from isodate import parse_duration, ISO8601Error
from requests import HTTPError
import soundcloud

from exceptions import ExecutionException, OptionsException, PermissionsException
from utils import get_stream_url, parse_authorization, parse_query, HOST, XML


class API:
    HOST = HOST
    REALM_NAME = 'SoundCloud'
    DEFAULT_HEADERS = {'Content-Type': 'application/xml'}
    DEFAULT_PARAMS = {
        'limit': 200,
        'client_id': 'MISSING',
    }
    DEFAULT_OPTIONS = {
        'shuffle': False,
        'relative': {},
    }

    def __init__(self, path, headers):
        location = urlparse(path)
        options_query, client_id = parse_authorization(headers['Authorization'])

        self.options = self.get_options(options_query)
        self.params = self.get_params(location.query, client_id=client_id)

    def get_options(self, query, defaults=DEFAULT_OPTIONS, **options):
        return {**defaults, **parse_query(query, depth=1), **options}

    def get_params(self, query, defaults=DEFAULT_PARAMS, **params):
        return {**defaults, **parse_query(query), **params}

    def preprocess_params(self, params, **options):
        processed = deepcopy(params)

        relative = options['relative']
        if not isinstance(relative, dict):
            raise OptionsException('`relative` option must have nested keys')

        for keys, duration in relative.items():
            *paths, key = filter(bool, keys.split('.'))
            parent = processed

            for path in paths:
                if not isinstance(parent.get(path), dict):
                    parent[path] = {}
                parent = parent[path]

            try:
                absolute = datetime.now() - parse_duration(duration)
            except ISO8601Error:
                raise OptionsException(
                    f'`relative` duration "{duration}" of key "{keys}" must conform to ISO 8601'
                )
            parent[key] = absolute.strftime('%Y-%m-%d %H:%M:%S')

        return {**params, **processed}

    def execute_request(self, path, client_id=None, **params):
        try:
            client = soundcloud.Client(client_id=client_id)
            return client.get(path, **params)

        except HTTPError as error:
            status_code = error.response.status_code
            bytes_message = error.response.content

            if status_code == 401:
                raise PermissionsException()

            raise ExecutionException(status_code, bytes_message)

    def postprocess_result(self, result, **options):
        if options['shuffle']:
            result = random.sample(result, len(result))

        return result

    def generate_response(self, result, path, *, client_id, **params):
        try:
            return (  # NOQA: E124
                XML('rss',
                    XML('channel',
                        XML('title', f'Results for {path}'),
                        XML('description', f'With parameters "{params}"'),
                        XML('link', f'https://{soundcloud.Client.host}{path}'),
                        XML('atom:link', f'{self.HOST}{path}'),

                        *[XML('item',
                            XML('title', item.title),
                            XML('description', item.description),
                            XML('enclosure', type='audio/mpeg', url=get_stream_url(item, client_id)),
                            XML('link', item.permalink_url),
                            XML('guid', item.id),
                        ) for item in result],
                    ),
                    version='2.0',
                    **{'xmlns:atom': 'http://www.w3.org/2005/Atom'},
                )
            )

        except AttributeError as attribute_error:
            return ExecutionException(bytes_message=str(attribute_error).encode())
