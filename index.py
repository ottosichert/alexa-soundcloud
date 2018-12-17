from http.server import BaseHTTPRequestHandler
import random
from urllib.parse import urlparse

import soundcloud

from utils import parse_authorization, parse_query, XML


class handler(BaseHTTPRequestHandler):
    REALM_NAME = 'SoundCloud'
    DEFAULT_HEADERS = {'Content-Type': 'application/xml'}
    DEFAULT_PARAMS = {'limit': 200}

    def do_HEAD(self):
        self.respond()

    def do_AUTHHEAD(self):
        self.respond(
            status_code=401,
            **{'WWW-Authenticate': f'Basic realm="{self.REALM_NAME}"'},
        )

    def do_GET(self):
        options_query, client_id = parse_authorization(self.headers['Authorization'])
        options = parse_query(options_query)
        location = urlparse(self.path)
        api_params = parse_query(location.query)
        params = {**self.DEFAULT_PARAMS, **api_params}

        try:
            client = soundcloud.Client(client_id=client_id)
            result = client.get(location.path, **params)
        except soundcloud.request.requests.HTTPError:
            return self.do_AUTHHEAD()

        if options.get('shuffle'):
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
