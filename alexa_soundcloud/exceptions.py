class BytesMixin:
    def __bytes__(self):
        return str(self).encode()


class ExecutionException(Exception):
    def __init__(self, status_code=500, bytes_message=b''):
        self.status_code = status_code
        self.bytes_message = bytes_message

    def __bytes__(self):
        return self.bytes_message


class OptionsException(BytesMixin, Exception):
    pass


class PermissionsException(BytesMixin, Exception):
    pass
