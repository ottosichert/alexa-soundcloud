from datetime import datetime
from http.server import BaseHTTPRequestHandler
import random
from urllib.parse import urlparse

from isodate import parse_duration, ISO8601Error
from requests import HTTPError
import soundcloud

from utils import parse_authorization, parse_query, XML


class handler(BaseHTTPRequestHandler):
    REALM_NAME = 'SoundCloud'
    DEFAULT_HEADERS = {'Content-Type': 'application/xml'}
    DEFAULT_PARAMS = {'limit': 200}
    DEFAULT_OPTIONS = {
        'shuffle': False,
        'relative': {},
    }

    def do_HEAD(self):
        self.respond()

    def do_AUTHHEAD(self):
        self.yell(
            status_code=401,
            **{'WWW-Authenticate': f'Basic realm="{self.REALM_NAME}"'},
        )

    def do_GET(self):
        location = urlparse(self.path)
        options_query, client_id = parse_authorization(self.headers['Authorization'])
        options = {**self.DEFAULT_OPTIONS, **parse_query(options_query, depth=1)}
        params = {**self.DEFAULT_PARAMS, **parse_query(location.query)}

        relative = options['relative']
        if not isinstance(relative, dict):
            return self.yell(body=b'`relative` option must have nested keys')

        for keys, duration in relative.items():
            *paths, key = filter(bool, keys.split('.'))
            parent = params

            for path in paths:
                if not isinstance(parent.get(path), dict):
                    parent[path] = {}
                parent = parent[path]

            try:
                absolute = datetime.now() - parse_duration(duration)
            except ISO8601Error:
                return self.yell(
                    body=f'`relative` duration "{duration}" of key "{keys}" must conform to ISO 8601'.encode()
                )
            parent[key] = absolute.strftime('%Y-%m-%d %H:%M:%S')

        try:
            client = soundcloud.Client(client_id=client_id)
            result = client.get(location.path, **params)
        except HTTPError as error:
            status_code = error.response.status_code
            if status_code == 401:
                return self.do_AUTHHEAD()
            return self.yell(status_code=status_code, body=error.response.content)

        if options['shuffle']:
            random.shuffle(result)

        root = (  # NOQA: E124
            XML('rss',
                XML('channel',
                    XML('title', f'Results for {location.path}'),
                    XML('description', f'With parameters "{params}"'),
                    XML('link', f'https://{client.host}{self.path}'),
                    XML('atom:link', 'https://alexa-soundcloud.now.sh{self.path}'),

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

        self.respond(body=bytes(root))

    def respond(self, status_code=200, body=None, **headers):
        self.send_response(status_code)

        for header, value in {**self.DEFAULT_HEADERS, **headers}.items():
            self.send_header(header, value)
        self.end_headers()

        if body:
            self.wfile.write(body)

    def yell(self, status_code=400, **kwargs):
        kwargs.setdefault('Content-Type', 'text/plain')
        self.respond(status_code=status_code, **kwargs)
