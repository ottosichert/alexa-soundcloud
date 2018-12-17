import base64
import re

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
