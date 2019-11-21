from datetime import datetime
import unittest
from unittest import mock

from alexa_soundcloud.api import API
from alexa_soundcloud.exceptions import OptionsException


class APIPreprocessTestCase(unittest.TestCase):
    @mock.patch('alexa_soundcloud.utils.datetime')
    def test_option_relative(self, mocked_datetime):
        mocked_datetime.now.return_value = datetime(2018, 1, 1)

        options = {'relative': {'foo': 'P1Y'}}
        params = API.preprocess_params({}, **options)

        self.assertIn('foo', params)
        self.assertEqual(params['foo'], '2017-01-01 00:00:00')

    def test_option_type_relative(self):
        with self.assertRaises(OptionsException):
            API.preprocess_params({}, relative='P1W')

        with self.assertRaises(OptionsException):
            API.preprocess_params({}, relative=True)

        with self.assertRaises(OptionsException):
            API.preprocess_params({}, relative={'foo': 'bar'})
