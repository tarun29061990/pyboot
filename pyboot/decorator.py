import logging
from functools import wraps

from flask import render_template
from flask import request
from werkzeug.exceptions import BadRequest

from pyboot.exception import NotFoundException, InvalidInputException, InvalidValueException, \
    AccessDeniedException, DuplicateValueException, InvalidStateException, AuthFailedException
from pyboot.model import HttpResponse
from pyboot.json import json_response


class Decorator(object):
    def init(self):
        pass


class Controller(Decorator):
    def __init__(self):
        self.not_found_template = None
        self.server_error_template = None
        self.access_denied_template = None

    def view_controller(self):
        def decorator(f):
            @wraps(f)
            def view_response_handler(*args, **kwargs):
                try:
                    return f(*args, **kwargs)
                except NotFoundException as e:
                    logging.warning("Not found [%s %s]: %s" % (request.method, request.url, e))
                    if self.not_found_template:
                        return render_template(self.not_found_template, exception=e), 404
                    else:
                        return "Not found [404]: " + str(e)
                except (InvalidInputException, InvalidValueException, InvalidStateException) as e:
                    logging.warning("Bad request [%s %s]: %s" % (request.method, request.url, e))
                    if self.server_error_template:
                        return render_template(self.server_error_template, exception=e), 400
                    else:
                        return "Server error [500]: " + str(e)
                except AccessDeniedException as e:
                    logging.warning("Access denied (Forbidden) [%s %s]: %s" % (request.method, request.url, e))
                    if self.access_denied_template:
                        return render_template(self.access_denied_template, exception=e), 403
                    else:
                        return "Access Denied [403]: " + str(e)
                except Exception as e:
                    logging.error("Internal error [%s %s]: %s" % (request.method, request.url, e))
                    logging.exception(e)
                    if self.server_error_template:
                        return render_template(self.server_error_template, exception=e), 500
                    else:
                        return "Server error [500]: " + str(e)

            return view_response_handler

        return decorator

    def api_controller(self):
        def decorator(f):
            @wraps(f)
            def api_response_handler(*args, **kwargs):
                try:
                    response = f(*args, **kwargs)
                    return response if response else json_response(HttpResponse())
                except (BadRequest, InvalidInputException, InvalidValueException) as e:
                    logging.warning("Bad request [%s %s]: %s" % (request.method, request.url, e))
                    return json_response(HttpResponse(code=400, message=str(e))), 400
                except NotFoundException as e:
                    logging.warning("Not found [%s %s]: %s" % (request.method, request.url, e))
                    return json_response(HttpResponse(code=404, message=str(e))), 404
                except DuplicateValueException as e:
                    logging.warning("Duplicate value: [%s %s]: %s" % (request.method, request.url, e))
                    return json_response(HttpResponse(code=409, message=str(e))), 409
                except AccessDeniedException as e:
                    logging.warning("Access denied (Forbidden) [%s %s]: %s" % (request.method, request.url, e))
                    return json_response(HttpResponse(code=403, message=str(e))), 403
                except AuthFailedException as e:
                    logging.warning("Authentication Failed [%s %s]: %s" % (request.method, request.url, e))
                    return json_response(HttpResponse(code=401, message=str(e))), 401
                except Exception as e:
                    logging.error("Internal error [%s %s]: %s" % (request.method, request.url, e))
                    logging.exception(e)
                    return json_response(HttpResponse(code=500, message="Internal error")), 500

            return api_response_handler

        return decorator
