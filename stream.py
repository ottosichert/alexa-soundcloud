from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import requests


class handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.respond()

    def do_GET(self):
        location = urlparse(self.path)
        track_id = location.path.split('/')[2]
        query = parse_qs(location.query)
        client_id = query.get('client_id', [""])[0]

        if not client_id or not track_id:
            return self.yell(body=b'Please provide a valid `client_id` as GET parameter!')

        try:
            track = requests.get(f'https://api-v2.soundcloud.com/tracks/{track_id}?client_id={client_id}').json()
            stream = next(filter(
                lambda transcoding: transcoding['format']['protocol'] == 'progressive',
                track['media']['transcodings'],
            ))['url']

            url = requests.get(f'{stream}?client_id={client_id}').json()['url']

        except requests.HTTPError:
            return self.yell(body=b'Invalid `client_id` or `track_id`!')

        return self.respond(
            status_code=302,
            location=url,
        )

    def respond(self, status_code=200, body=None, **headers):
        self.send_response(status_code)

        for header, value in headers.items():
            self.send_header(header, value)
        self.end_headers()

        if body:
            self.wfile.write(body)

    def yell(self, status_code=400, **kwargs):
        kwargs.setdefault('Content-Type', 'text/plain')
        self.respond(status_code=status_code, **kwargs)
