import logging
from functools import wraps

from flask import request
from werkzeug.exceptions import BadRequest

from common.exception import NotFoundException, InvalidInputException, InvalidValueException, AccessDeniedException, \
    DuplicateValueException, UnauthorizedException
from json import HttpResponse
from util.json import json_response


class Decorator(object):
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
            cls._instance.init()
        return cls._instance

    def init(self):
        pass


class Controller(Decorator):
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
                except UnauthorizedException as e:
                    logging.warning("Unauthorized (Forbidden) [%s %s]: %s" % (request.method, request.url, e))
                    return json_response(HttpResponse(code=401, message=str(e))), 401
                except Exception as e:
                    logging.error("Internal error [%s %s]: %s" % (request.method, request.url, e))
                    logging.exception(e)
                    return json_response(HttpResponse(code=500, message="Internal error")), 500

            return api_response_handler

        return decorator

# class Security(Decorator):
#     def auth_required(self):
#         def decorator(f):
#             @wraps(f)
#             def auth_handler(*args, **kwargs):
#                 if not g.employee_cookie:
#                     raise AuthenticationFailedException("Authentication failed")
#                 return f(*args, **kwargs)
#
#             return auth_handler
#
#         return decorator
#
# class Permissions(Decorator):
#     def __init__(self):
#         pass
#
#     def init(self):
#         pass
#
#     def __validate_permission(self, user, expected_permissions):
#         if not user or not expected_permissions:
#             raise UnauthorizedException("Entity name or permission name can not be empty")
#         if not user.id and user.role:
#             raise UnauthorizedException("User name and role not found")
#         # Add check for designer.
#         if user.role == LaunchpadRole.INTERIOR_DESIGNER.value:
#             user_permissions = BouncerService().get_role_permissions_list(LaunchpadRole.INTERIOR_DESIGNER.value)
#         else:
#             bouncer_id = user.id
#             user_permissions = BouncerService().get_user_permissions_list(bouncer_id)
#         is_permission_found = False
#
#         for permission in expected_permissions:
#             if user_permissions and permission in user_permissions:
#                 is_permission_found = True
#             else:
#                 raise AccessDeniedException("permission : %s couldn't found for user" % permission)
#
#         if not is_permission_found:
#             raise AccessDeniedException(
#                 "Couldn't found required permissions : %s for user" % json.dumps(expected_permissions))
#
#         return True
#
#     def required(self, *permission):
#         def decorator(f):
#             @wraps(f)
#             def permission_handler(*args, **kwargs):
#                 if self.__validate_permission(g.user, permission):
#                     return f(*args, **kwargs)
#                 else:
#                     raise AccessDeniedException()
#
#             return permission_handler
#
#         return decorator
