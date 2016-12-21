import json

import datetime
from flask import Response

from pyboot.util import TypeUtil, DateTimeUtil, DateUtil, TimeUtil
from pyboot.conf import MIME_TYPE_JSON
from pyboot.core import DictSerializable


# def json_response(obj, status=200, mimetype=MIME_TYPE_JSON):
#     if isinstance(obj, str):
#         response = obj
#     elif isinstance(obj, list):
#         final_obj = []
#         for o in obj:
#             if isinstance(o, DictSerializable):
#                 final_obj.append(o.to_dict_deep())
#             else:
#                 final_obj.append(o)
#         response = dump_json(final_obj)
#     elif isinstance(obj, DictSerializable):
#         response = dump_json(obj.to_dict_deep())
#     else:
#         response = dump_json(obj)
#     return Response(response=response, mimetype=mimetype, status=status)
#
#
# def __serialize_object(obj):
#     if isinstance(obj, bytes):
#         return obj.decode("utf-8")
#     elif issubclass(obj.__class__, DictSerializable):
#         return obj.to_dict_deep()
#     elif isinstance(obj, datetime.datetime):
#         return DateTimeUtil.dt_to_iso(obj)
#     elif isinstance(obj, datetime.date):
#         return DateUtil.date_to_iso(obj)
#     elif isinstance(obj, datetime.time):
#         return TimeUtil.time_to_iso(obj)
#
#     elif issubclass(obj.__class__, decimal.Decimal):
#         return float(obj)
#     else:
#         return iter(obj)


def json_response(obj, status=200, mimetype=MIME_TYPE_JSON):
    return Response(response=dump_json(obj), mimetype=mimetype, status=status)


def __to_json_dict(obj):
    if isinstance(obj, bytes):
        return obj.decode("utf-8")
    elif issubclass(obj.__class__, DictSerializable):
        return obj.to_dict_deep()
    elif isinstance(obj, datetime.datetime):
        return DateTimeUtil.dt_to_iso(obj)
    elif isinstance(obj, datetime.date):
        return DateUtil.date_to_iso(obj)
    elif isinstance(obj, datetime.time):
        return TimeUtil.time_to_iso(obj)
    else:
        return TypeUtil.cast(obj, type(obj))


def dump_json(obj) -> str:
    return json.dumps(obj, default=__to_json_dict)


def load_json(obj_str: str):
    return json.loads(obj_str)
