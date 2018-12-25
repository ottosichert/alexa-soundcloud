import random
from urllib.parse import urlparse

from requests import HTTPError
import soundcloud

from .exceptions import ExecutionException, OptionsException, PermissionsException
from .utils import parse_authorization, parse_query, RELATIVE, traverse_paths, XML


class API:
    HOST = 'https://alexa-soundcloud.now.sh'
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

    @classmethod
    def get_configuration(cls, path, headers):
        location = urlparse(path)
        options_query, client_id = parse_authorization(headers['Authorization'])

        options = {**cls.DEFAULT_OPTIONS, **parse_query(options_query, depth=1)}
        params = {**cls.DEFAULT_PARAMS, **parse_query(location.query), 'client_id': client_id}
        return options, params

    @classmethod
    def preprocess_params(cls, params, **options):
        relative = options['relative']
        if not isinstance(relative, dict):
            raise OptionsException('`relative` option must have nested keys')

        processed = traverse_paths(params, relative, processing=RELATIVE)
        return {**params, **processed}

    @classmethod
    def execute_request(cls, path, client_id=None, **params):
        try:
            client = soundcloud.Client(client_id=client_id)
            return client.get(path, **params)

        except HTTPError as error:
            status_code = error.response.status_code
            bytes_message = error.response.content

            if status_code == 401:
                raise PermissionsException()

            raise ExecutionException(status_code, bytes_message)

    @classmethod
    def postprocess_result(cls, result, **options):
        if options['shuffle']:
            result = random.sample(result, len(result))

        return result

    @classmethod
    def generate_response(cls, result, path, *, client_id, **params):
        try:
            return (  # NOQA: E124
                XML('rss',
                    XML('channel',
                        XML('title', f'Results for {path}'),
                        XML('description', f'With parameters "{params}"'),
                        XML('link', f'https://{soundcloud.Client.host}{path}'),
                        XML('atom:link', f'{cls.HOST}{path}'),

                        *[XML('item',
                            XML('title', item.title),
                            XML('description', item.description),
                            XML('enclosure', type='audio/mpeg', url=f'{item.stream_url}?client_id={client_id}'),
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
