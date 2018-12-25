from http.server import BaseHTTPRequestHandler

from .api import API
from .exceptions import ExecutionException, OptionsException, PermissionsException


class handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.respond()

    def do_AUTHHEAD(self):
        self.respond(
            status_code=401,
            headers={'WWW-Authenticate': f'Basic realm="{API.REALM_NAME}"'},
            body=(
                b'Please provide valid `options` as username and a SoundClound `client_id` as password.\n'
                b'The URL path will be appended to the SoundCloud API call.\n\n'
                b'For more information see https://github.com/ottosichert/alexa-soundcloud'
            ),
        )

    def do_GET(self):
        path = self.path
        options, params = API.get_configuration(path, self.headers)

        try:
            processed_params = API.preprocess_params(params, **options)
            result = API.execute_request(path, **processed_params)
            processed_result = API.postprocess_result(result, **options)
            response = API.generate_response(processed_result, path, **processed_params)

        except OptionsException as options_exception:
            return self.respond(
                status_code=400,
                body=bytes(options_exception),
            )

        except PermissionsException:
            return self.do_AUTHHEAD()

        except ExecutionException as execution_exception:
            return self.respond(
                status_code=execution_exception.status_code,
                headers={'Content-Type': 'application/json'},
                body=bytes(execution_exception),
            )

        return self.respond(
            body=bytes(response),
            headers={'Content-Type': 'application/xml'},
        )

    def respond(self, status_code=200, body=None, headers=None):
        self.send_response(status_code)

        for header, value in {**API.DEFAULT_HEADERS, **(headers or {})}.items():
            self.send_header(header, value)
        self.end_headers()

        if body:
            self.wfile.write(body)
