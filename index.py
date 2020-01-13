from http.server import BaseHTTPRequestHandler

from api import API
from exceptions import ExecutionException, OptionsException, PermissionsException


class handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.respond()

    def do_AUTHHEAD(self):
        self.yell(
            status_code=401,
            **{'WWW-Authenticate': f'Basic realm="{API.REALM_NAME}"'},
            body=b'Please provide valid `options` as username and a SoundCloud `client_id` as password.\n'
            b'The URL path will be appended to the SoundCloud API call.\n\n'
            b'For more information see https://github.com/ottosichert/alexa-soundcloud',
        )

    def do_GET(self):
        path = self.path
        api = API(path, self.headers)
        options = api.options
        params = api.params

        try:
            processed_params = api.preprocess_params(params, **options)
            result = api.execute_request(path, **processed_params)
            result = api.postprocess_result(result, **options)
            response = api.generate_response(result, path, **processed_params)

        except OptionsException as options_exception:
            return self.yell(body=bytes(options_exception))

        except PermissionsException:
            return self.do_AUTHHEAD()

        except ExecutionException as execution_exception:
            return self.yell(
                status_code=execution_exception.status_code,
                body=bytes(execution_exception)
            )

        return self.respond(body=bytes(response))

    def respond(self, status_code=200, body=None, **headers):
        self.send_response(status_code)

        for header, value in {**API.DEFAULT_HEADERS, **headers}.items():
            self.send_header(header, value)
        self.end_headers()

        if body:
            self.wfile.write(body)

    def yell(self, status_code=400, **kwargs):
        kwargs.setdefault('Content-Type', 'text/plain')
        self.respond(status_code=status_code, **kwargs)
