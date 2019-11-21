import base64
import unittest

from alexa_soundcloud.api import API


class APIConfigurationTestCase(unittest.TestCase):
    def create_headers(self, username='', password=''):
        token = base64.b64encode(f'{username}:{password}'.encode()).decode()
        return {'Authorization': f'Basic {token}'}

    def test_configuration_params(self):
        q = 'dub techno'
        date = '2018-01-01 00:00:00'
        url = f'https://alexa-soundcloud.now.sh/tracks?q={q}&created_at.from={date}'
        _, params = API.get_configuration(url, self.create_headers())

        self.assertIn('q', params)
        self.assertEqual(params['q'], q)

        self.assertIn('created_at', params)
        created_at = params['created_at']
        self.assertIn('from', created_at)
        self.assertEqual(created_at['from'], date)

    def test_configuration_client_id(self):
        url = 'https://alexa-soundcloud.now.sh/tracks'
        client_id = 'abcdef123456'
        _, params = API.get_configuration(url, self.create_headers(password=client_id))

        self.assertIn('client_id', params)
        self.assertEqual(params['client_id'], client_id)

    def test_configuration_options(self):
        url = 'https://alexa-soundcloud.now.sh/tracks'
        options = 'foo&bar=baz'
        options, _ = API.get_configuration(url, self.create_headers(username=options))

        self.assertIn('foo', options)
        self.assertTrue(options['foo'])

        self.assertIn('bar', options)
        self.assertEqual(options['bar'], 'baz')

    def test_configuration_nested_options(self):
        url = 'https://alexa-soundcloud.now.sh/tracks'
        options = 'foo.bar.baz=qux'
        options, _ = API.get_configuration(url, self.create_headers(username=options))

        self.assertIn('foo', options)
        foo = options['foo']
        self.assertIn('bar.baz', foo)
        self.assertEqual(foo['bar.baz'], 'qux')
