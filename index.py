from http.server import BaseHTTPRequestHandler
import random

import soundcloud

from utils import parse_authorization, XML


class handler(BaseHTTPRequestHandler):
    REALM_NAME = 'SoundCloud'
    DEFAULT_HEADERS = {'Content-Type': 'application/xml'}

    def do_HEAD(self):
        self.respond()

    def do_AUTHHEAD(self):
        self.respond(
            status_code=401,
            **{'WWW-Authenticate': f'Basic realm="{self.REALM_NAME}"'},
        )

    def do_GET(self):
        username, client_id = parse_authorization(self.headers['Authorization'])

        try:
            client = soundcloud.Client(client_id=client_id)
            user_id = client.get('/resolve', url=f'https://soundcloud.com/{username}').id
        except soundcloud.request.requests.HTTPError:
            return self.do_AUTHHEAD()

        # TODO: Add more functionality
        likes = client.get(f'/users/{user_id}/favorites', limit=200)
        random.shuffle(likes)

        root = (  # NOQA: E124
            XML('rss',
                XML('channel',
                    XML('title', f'{username}\'s likes'),
                    XML('description', 'Your shuffled SoundCloud favourites as RSS feed!'),
                    XML('link', f'https://soundcloud.com/{username}/likes'),
                    XML('atom:link', 'https://alexa-soundcloud.now.sh'),

                    *[XML('item',
                        XML('title', like.title),
                        XML('description', like.description),
                        XML('enclosure', type='audio/mpeg', url=f'{like.stream_url}?client_id={client_id}'),
                        XML('link', like.permalink_url),
                        XML('guid', like.id),
                    ) for like in likes],
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
