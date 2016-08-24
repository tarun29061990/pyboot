import datetime
import json

from flask import Response

from pyboot.conf import MIME_TYPE_JSON
from pyboot.json import JSONSerializable
from pyboot.model import Model
from pyboot.util.common import DateTimeUtil, DateUtil, TimeUtil


def json_response(obj, include=None, status=200, mimetype=MIME_TYPE_JSON):
    if isinstance(obj, str):
        response = obj
    elif isinstance(obj, list):
        final_obj = []
        for o in obj:
            if isinstance(o, JSONSerializable):
                final_obj.append(o.to_json_dict(include))
            else:
                final_obj.append(o)
        response = dump_json(final_obj)
    elif isinstance(obj, JSONSerializable):
        response = dump_json(obj.to_json_dict(include))
    else:
        response = dump_json(obj)
    return Response(response=response, mimetype=mimetype, status=status)


def __serialize_object(obj):
    if isinstance(obj, bytes):
        return obj.decode("utf-8")
    elif isinstance(obj, datetime.datetime):
        return DateTimeUtil.dt_to_iso(obj)
    elif isinstance(obj, datetime.date):
        return DateUtil.date_to_iso(obj)
    elif isinstance(obj, datetime.time):
        return TimeUtil.time_to_iso(obj)
    elif issubclass(obj.__class__, Model):
        return obj.to_json_dict()
    elif issubclass(obj.__class__, JSONSerializable):
        return obj.to_json_dict()
    else:
        return iter(obj)


def dump_json(obj):
    return json.dumps(obj, default=__serialize_object)


def load_json(obj):
    return json.loads(obj)
