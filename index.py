from http.server import BaseHTTPRequestHandler
from io import BytesIO
import random
from xml.etree.ElementTree import Element, ElementTree, SubElement

import soundcloud

from utils import parse_authorization


class handler(BaseHTTPRequestHandler):
    REALM_NAME = 'SoundCloud'
    DEFAULT_HEADERS = {'Content-Type': 'application/xml'}

    def do_HEAD(self):
        self.respond()

    def do_AUTHHEAD(self):
        self.respond(
            status_code=401,
            headers={'WWW-Authenticate': f'Basic realm="{self.REALM_NAME}"'},
        )

    def do_GET(self):
        authorization = self.headers['Authorization']
        if authorization is None:
            return self.do_AUTHHEAD()

        username, client_id = parse_authorization(authorization)
        if not username or not client_id:
            return self.do_AUTHHEAD()

        # TODO: move this to utils.py
        client = soundcloud.Client(client_id=client_id)

        user_id = client.get('/resolve', url=f'https://soundcloud.com/{username}').id

        likes = client.get(f'/users/{user_id}/favorites', limit=200)
        random.shuffle(likes)

        root = Element('rss')
        root.set('version', '2.0')
        root.set('xmlns:atom', 'http://www.w3.org/2005/Atom')

        channel = SubElement(root, 'channel')
        SubElement(channel, 'title').text = SubElement(channel, 'description').text = f'{username}\'s likes'
        SubElement(channel, 'link').text = SubElement(channel, 'atom:link').text = \
            f'https://soundcloud.com/{username}/likes'

        for like in likes:
            item = SubElement(channel, 'item')
            SubElement(item, 'title').text = like.title
            SubElement(item, 'description').text = like.description
            url = f'{like.stream_url}?client_id={client_id}'

            enclosure = SubElement(item, 'enclosure')
            enclosure.set('type', 'audio/mpeg')
            enclosure.set('url', url)
            SubElement(item, 'link').text = SubElement(item, 'guid').text = url

        # convert XML tree to string with XML declaratiom
        document = BytesIO()
        tree = ElementTree(root)
        tree.write(document, encoding='utf-8', xml_declaration=True)
        body = document.getvalue()

        self.respond(body=body)

    def respond(self, status_code=200, headers=None, body=None):
        self.send_response(status_code)

        all_headers = self.DEFAULT_HEADERS.copy()
        if headers:
            all_headers.update(headers)
        for header, value in all_headers.items():
            self.send_header(header, value)
        self.end_headers()

        if body:
            self.wfile.write(body)
