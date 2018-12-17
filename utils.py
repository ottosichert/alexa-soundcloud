import base64
import re

TOKEN_PATTERN = re.compile(r'^\s*(?P<protocol>\w+)\s+(?P<token>[^\s]+)\s*$')

def parse_authorization(header):
    username = password = ''
    match = TOKEN_PATTERN.match(header)

    if match:
        token = match['token']

        try:
            decoded = base64.b64decode(token).decode()
        except base64.binascii.Error:
            decoded = ''

        try:
            separator = decoded.index(':')
        except ValueError:
            separator = 0

        username = decoded[:separator]
        password = decoded[separator+1:]

    return username, password
