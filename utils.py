import base64
from io import BytesIO
import re
from xml.etree.ElementTree import Element, ElementTree

TOKEN_PATTERN = re.compile(r'^\s*(?P<protocol>\w+)\s+(?P<token>[^\s]+)\s*$')


def parse_authorization(header, username=None, password=None):
    match = header and TOKEN_PATTERN.match(header)
    if not match:
        return username, password

    token = match['token']

    try:
        decoded = base64.b64decode(token).decode()
        separator = decoded.index(':')
    except (base64.binascii.Error, UnicodeDecodeError, ValueError):
        return username, password

    username = decoded[:separator] or username
    password = decoded[separator+1:] or password

    return username, password


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
