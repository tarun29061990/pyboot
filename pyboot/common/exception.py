class NotFoundException(Exception):
    def __init__(self, message=None):
        super(NotFoundException, self).__init__(message)


class InvalidInputException(Exception):
    def __init__(self, message=None):
        super(InvalidInputException, self).__init__(message)


class InvalidValueException(Exception):
    def __init__(self, message=None):
        super(InvalidValueException, self).__init__(message)


class DuplicateValueException(Exception):
    def __init__(self, message=None):
        super(DuplicateValueException, self).__init__(message)


class InvalidStateException(Exception):
    def __init__(self, message=None):
        super(InvalidStateException, self).__init__(message)


class UnauthorizedException(Exception):
    def __init__(self, message):
        super(UnauthorizedException, self).__init__(message)


class AccessDeniedException(Exception):
    def __init__(self, message=None):
        super(AccessDeniedException, self).__init__(message)


class AuthenticationFailedException(Exception):
    def __init__(self, message=None):
        super(AuthenticationFailedException, self).__init__(message)


# class HttpError(Exception):
#     def __init__(self, message=None):
#         super(HttpError, self).__init__(message)

class MultipleRowsFoundException(Exception):
    def __init__(self, message=None):
        super(MultipleRowsFoundException, self).__init__(message)
