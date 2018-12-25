import base64
from copy import deepcopy
from datetime import datetime
from io import BytesIO
import re
from urllib.parse import parse_qs
from xml.etree.ElementTree import Element, ElementTree

from isodate import parse_duration, ISO8601Error

from .exceptions import OptionsException

AUTHORIZATION_PATTERN = re.compile(r'^\s*(?P<protocol>\w+)\s+(?P<token>[^\s]+)\s*$')


def parse_authorization(header, username='', password=''):
    match = header and AUTHORIZATION_PATTERN.match(header)
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


RELATIVE = 'RELATIVE'
LAST_ITEM = 'LAST_ITEM'


def traverse_paths(defaults, pairs, depth=-1, processing=LAST_ITEM):
    processed = deepcopy(defaults)

    for keys, value in pairs.items():
        *paths, key = keys.split('.', maxsplit=depth)
        parent = processed

        for path in paths:
            if not isinstance(parent.get(path), dict):
                parent[path] = {}
            parent = parent[path]

        if processing == RELATIVE:
            try:
                absolute = datetime.now() - parse_duration(value)
            except ISO8601Error:
                raise OptionsException(
                    f'`relative` duration "{value}" of key "{keys}" must conform to ISO 8601'
                )
            parent[key] = absolute.strftime('%Y-%m-%d %H:%M:%S')

        elif processing == LAST_ITEM:
            parent[key] = value[-1] or True

    return processed


def parse_query(query_string, depth=-1):
    query = parse_qs(query_string, keep_blank_values=True)
    return traverse_paths({}, query, depth=depth, processing=LAST_ITEM)


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
