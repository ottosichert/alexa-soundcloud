import base64
from io import BytesIO
import re
from urllib.parse import parse_qs
from xml.etree.ElementTree import Element, ElementTree

HOST = 'https://alexa-soundcloud.now.sh'
STREAM_URL = f'{HOST}/stream'
TOKEN_PATTERN = re.compile(r'^\s*(?P<protocol>\w+)\s+(?P<token>[^\s]+)\s*$')


def get_stream_url(item, client_id):
    # As documented in https://developers.soundcloud.com/docs/api/reference#tracks it should be item.stream_url
    # however the API sometimes throws 401, using stream.py proxy instead

    # return f'{item.stream_url}?client_id={client_id}'

    return f'{STREAM_URL}/{item.id}?client_id={client_id}'


def parse_authorization(header, username='', password=''):
    match = header and TOKEN_PATTERN.match(header)
    if not match:
        return username, password

    token = match['token']

    try:
        decoded = base64.b64decode(token).decode()
        separator = decoded.index(':')
    except (base64.binascii.Error, UnicodeDecodeError, ValueError):
        return username, password

    username = decoded[:separator]
    password = decoded[separator+1:]

    return username, password


def parse_query(query_string, depth=-1):
    parsed = {}
    query = parse_qs(query_string, keep_blank_values=True)

    for keys, values in query.items():
        *paths, key = filter(bool, keys.split('.', maxsplit=depth))
        parent = parsed

        for path in paths:
            if not isinstance(parent.get(path), dict):
                parent[path] = {}
            parent = parent[path]

        parent[key] = values[0] or True if len(values) == 1 else values

    return parsed


class XML:
    def __init__(self, tag, *children, **attributes):
        self.element = Element(tag, **attributes)

        for child in children:
            if isinstance(child, XML):
                self.element.append(child.element)
            else:
                self.element.text = (self.element.text or '') + str(child)

    def __bytes__(self):
        document = BytesIO()
        tree = ElementTree(self.element)
        tree.write(document, encoding='utf-8', xml_declaration=True)
        return document.getvalue()


class BytesMixin:
    def __bytes__(self):
        return str(self).encode()
