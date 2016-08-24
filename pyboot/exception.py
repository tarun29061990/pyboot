class NotFoundException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class InvalidInputException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class InvalidValueException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class DuplicateValueException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class InvalidStateException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class AuthFailedException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class AccessDeniedException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class MultipleRowsFoundException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class HttpError(Exception):
    def __init__(self, message=None):
        super().__init__(message)
