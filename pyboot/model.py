import decimal

import datetime

from pyboot.core import JSONSerializable
from pyboot.util import Parser, DateTimeUtil, Validator, DateUtil


# TYPE_INT = "int"
# TYPE_FLOAT = "float"
# TYPE_BOOL = "bool"
# TYPE_DECIMAL = "decimal"
# TYPE_STR = "str"
# TYPE_DATETIME = "datetime"
# TYPE_DATE = "date"
# TYPE_ENUM = "enum"
# TYPE_LIST = "list"
# TYPE_OBJ = "obj"
# TYPE_UNKNOWN = "unknown"


class HttpResponse(JSONSerializable):
    def __init__(self, code: int = 0, message: str = "Success"):
        self.code = code
        self.message = message

    def to_json_dict(self, include: list = None) -> dict:
        json_dict = super().to_json_dict(include)
        json_dict["code"] = self.code
        json_dict["message"] = self.message
        return json_dict


class Model(JSONSerializable):
    _structure = None

    # _required = None
    # _defaults = None

    @classmethod
    def _get_structure(cls):
        return cls._structure

    def _to_dict_field(self, obj_dict, name: str, obj_type=None):
        if not name or name not in self.__dict__: return
        value = getattr(self, name)
        if obj_type is str:
            obj_dict[name] = Parser.str(value)
        elif obj_type == int:
            obj_dict[name] = Parser.int(value)
        elif obj_type is float or obj_type is decimal.Decimal:
            obj_dict[name] = Parser.float(value)
        elif obj_type is bool:
            obj_dict[name] = Parser.bool(value)
        elif obj_type is datetime.datetime:
            if isinstance(value, str):
                obj_dict[name] = DateTimeUtil.iso_to_dt_local(value)
            else:
                obj_dict[name] = Validator.datetime(value)
        elif obj_type is datetime.date:
            if isinstance(value, str):
                obj_dict[name] = DateUtil.iso_to_date(value)
            else:
                obj_dict[name] = Validator.date(value)
        elif obj_type is None:
            obj_dict[name] = value
        else:
            obj_dict[name] = value

    def _from_dict_field(self, obj_dict: dict, name: str, obj_type=None):
        if not name or not obj_dict or name not in obj_dict: return
        value = obj_dict.get(name)
        if obj_type is str:
            setattr(self, name, Parser.str(value))
        elif obj_type is int:
            setattr(self, name, Parser.int(value))
        elif obj_type is float or obj_type is decimal.Decimal:
            setattr(self, name, Parser.float(value))
        elif obj_type is bool:
            setattr(self, name, Parser.bool(value))
        elif obj_type is datetime.datetime:
            if isinstance(value, str):
                setattr(self, name, DateTimeUtil.iso_to_dt_local(value))
            else:
                setattr(self, name, Validator.datetime(value))
        elif obj_type is datetime.date:
            if isinstance(value, str):
                setattr(self, name, DateUtil.iso_to_date(value))
            else:
                setattr(self, name, Validator.date(value))
        elif obj_type is None:
            setattr(self, name, value)
        else:
            setattr(self, name, value)

    def to_dict(self):
        obj_dict = {}
        structure = self.__class__._get_structure()
        if not structure: return obj_dict
        for field_name in structure.keys():
            self._to_dict_field(obj_dict, field_name, structure[field_name])
        return obj_dict

    def from_dict(self, obj_dict: dict):
        if not obj_dict: return

        structure = self.__class__._get_structure()
        if not structure: return self
        for field_name in structure:
            self._from_dict_field(obj_dict, field_name, structure[field_name])
        return self

    def to_json_dict(self, include: list = None) -> dict:
        json_dict = self.to_dict()

        structure = self.__class__._get_structure()
        if not structure: return json_dict
        for field_name in structure.keys():
            obj_type = structure[field_name]
            if issubclass(obj_type, object):
                self._include_obj(json_dict, include, field_name)
            elif obj_type is list:
                self._include_obj_list(json_dict, include, field_name)
        return json_dict

    def from_json_dict(self, json_dict: dict):
        self.from_dict(json_dict)

        structure = self.__class__._get_structure()
        if not structure: return self
        for field_name in structure:
            obj_type = structure[field_name]
            if issubclass(obj_type, object):
                self._exclude_obj(json_dict, field_name)
        return self

    def _include_obj_list(self, json_dict: dict, include: list, name: str):
        json_list = []
        obj_list = getattr(self, name, None) if include and name in include else None
        if obj_list and isinstance(obj_list, list):
            for obj in obj_list:
                if isinstance(obj, JSONSerializable):
                    json_list.append(obj.to_json_dict())
                else:
                    json_list.append(obj)
        json_dict[name] = json_list

    def _include_obj(self, json_dict: dict, include: list, name: str):
        if not include: include = []
        field_name = name + "_id"

        sub_obj = getattr(self, name, None) if include and name in include else None
        value = getattr(self, field_name, None) if field_name in self.__dict__ else None
        if sub_obj:
            if isinstance(sub_obj, JSONSerializable): json_dict[name] = sub_obj.to_json_dict()
        elif value:
            json_dict[name] = {"id": value}
        elif name in include:
            json_dict[name] = None

        if field_name in json_dict: del json_dict[field_name]

    def _exclude_obj(self, json_dict: dict, name: str):
        if not json_dict or name not in json_dict: return
        obj = json_dict[name]
        field_name = name + "_id"
        if "id" in obj and field_name in self.__class__._structure: setattr(self, field_name, obj["id"])
