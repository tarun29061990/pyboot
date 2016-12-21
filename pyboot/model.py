import logging

from pyboot.core import DictSerializable
from pyboot.exception import InvalidValueException
from pyboot.util import TypeUtil, ClassUtil


class HttpResponse(DictSerializable):
    def __init__(self, code: int = 0, message: str = "Success"):
        self.code = code
        self.message = message

    def to_dict(self) -> dict:
        obj_dict = super().to_dict_deep()
        obj_dict["code"] = self.code
        obj_dict["message"] = self.message
        return obj_dict

    def to_dict_deep(self):
        return self.to_dict()


class Model(DictSerializable):
    _structure = None

    @classmethod
    def _get_structure(cls):
        return cls._structure

    def _to_dict_field(self, obj_dict, field_name: str, value_type=None):
        if field_name is None or field_name not in self.__dict__: return

        value = getattr(self, field_name, None)
        if value is not None:
            obj_dict[field_name] = TypeUtil.cast(value, value_type)

    def _from_dict_field(self, obj_dict: dict, field_name: str, value_type=None):
        if not field_name or not obj_dict or field_name not in obj_dict: return

        value = obj_dict.get(field_name)
        if value is not None:
            setattr(self, field_name, TypeUtil.cast(value, value_type))

    def to_dict(self):
        obj_dict = {}
        structure = self.__class__._get_structure()  # type: dict
        if not structure: return obj_dict
        for key, value_type in structure.items():
            self._to_dict_field(obj_dict, key, value_type)
        return obj_dict

    def from_dict(self, obj_dict: dict):
        if not obj_dict: return

        structure = self.__class__._get_structure()  # type: dict
        if not structure: return self
        for key, value_type in structure.items():
            self._from_dict_field(obj_dict, key, value_type)
        return self

    def to_dict_deep(self) -> dict:
        obj_dict = {}
        structure = self.__class__._get_structure()  # type: dict
        if not structure: return obj_dict

        for key, value_type in structure.items():
            if value_type is None: continue
            if type(value_type) != type: value_type = type(value_type)

            value = getattr(self, key, None)
            if value_type is list:
                converted_value = self.serialize_list(key, value, structure[key])
            elif value_type is dict:
                converted_value = self.serialize_dict(key, value, structure[key])
            elif issubclass(value_type, Model):
                converted_value = self.serialize_model(key, value, structure[key])
            else:
                converted_value = TypeUtil.cast(value, value_type)

            obj_dict[key] = converted_value

        return obj_dict

    def from_dict_deep(self, obj_dict: dict):
        structure = self.__class__._get_structure()
        if not structure: return self

        for key, value_type in structure.items():
            if value_type is None: continue
            if type(value_type) != type: value_type = type(value_type)

            value = obj_dict.get(key)
            if value_type is list:
                converted_value = self.deserialize_list(key, value, structure[key])
            elif value_type is dict:
                converted_value = self.deserialize_dict(key, value, structure[key])
            elif issubclass(value_type, Model):
                converted_value = self.deserialize_model(key, value, structure[key])
            else:
                converted_value = TypeUtil.cast(value, value_type)

            setattr(self, key, converted_value)
        return self

    def serialize_list(self, field_name, value_list: list, structure: list):
        if value_list is None or structure is None: return

        value_type = structure[0]
        if not value_type: return
        if type(value_type) != type: value_type = type(value_type)

        return_list = []
        for value in value_list:
            if type(value) != value_type:
                raise InvalidValueException(
                    "Type mismatch for field '%s'. Value type '%s' does not match with defined type '%s'" % (
                        field_name, type(value), value_type))

            if value_type is list:
                converted_value = self.serialize_list(field_name, value, structure[0])
            elif value_type is dict:
                converted_value = self.serialize_dict(field_name, value, structure[0])
            elif issubclass(value_type, Model):
                converted_value = self.serialize_model(field_name, value, structure[0])
            else:
                converted_value = TypeUtil.cast(value, value_type)

            if converted_value is not None:
                return_list.append(converted_value)
        return return_list

    def serialize_dict(self, field_name, value_dict: dict, structure: dict):
        if value_dict is None or structure is None: return
        if type(value_dict) is not dict:
            raise InvalidValueException(
                "Type mismatch for field '%s'. Value type '%s' does not match with defined type '%s'" % (
                    field_name, type(value_dict), dict))

        return_dict = {}
        for key, value_type in structure.items():
            if type(value_type) != type: value_type = type(value_type)
            if key in value_dict: value = value_dict[key]
            if not value: continue

            if value_type is list:
                converted_value = self.serialize_list(field_name, value, structure[key])
            elif value_type is dict:
                converted_value = self.serialize_dict(field_name, value, structure[key])
            elif issubclass(value_type, Model):
                converted_value = self.serialize_model(field_name, value, structure[key])
            else:
                converted_value = TypeUtil.cast(value, value_type)
                if type(converted_value) != value_type:
                    raise InvalidValueException(
                        "Type mismatch for field '%s'. Value type '%s' does not match with defined type '%s'" % (
                            key, type(value_type), value_type))

            return_dict[key] = converted_value
        return return_dict

    def serialize_model(self, field_name, value_obj, value_type):
        if value_obj is None or value_type is None: return

        if issubclass(value_type, Model):
            if value_type != Model and type(value_obj) != value_type:
                raise InvalidValueException(
                    "Type mismatch for field '%s'. Value type '%s' does not match with defined type '%s'" % (
                        field_name, type(value_obj), value_type))
            return value_obj.to_dict_deep()
        else:
            return value_obj

    def deserialize_list(self, field_name, value_list: list, structure: list):
        if value_list is None or structure is None: return

        value_type = structure[0]
        if not value_type: return
        if type(value_type) != type: value_type = type(value_type)

        return_list = []
        for value in value_list:
            if value_type is list:
                converted_value = self.deserialize_list(field_name, value, structure[0])
            elif value_type is dict:
                converted_value = self.deserialize_dict(field_name, value, structure[0])
            elif issubclass(value_type, Model):
                converted_value = self.deserialize_model(field_name, value, structure[0])
            else:
                converted_value = TypeUtil.cast(value, value_type)

            if type(converted_value) != value_type:
                raise InvalidValueException(
                    "Type mismatch for field '%s'. Value type '%s' does not match with defined type '%s'" % (
                        field_name, type(value), value_type))

            if converted_value is not None:
                return_list.append(converted_value)
        return return_list

    def deserialize_dict(self, field_name, value_dict: dict, structure: dict):
        if value_dict is None or structure is None: return
        return_dict = {}
        for key, value_type in structure.items():
            if type(value_type) != type: value_type = type(value_type)
            if key in value_dict: value = value_dict[key]
            if not value: continue

            if value_type is list:
                converted_value = self.deserialize_list(field_name, value, structure[key])
            elif value_type is dict:
                converted_value = self.deserialize_dict(field_name, value, structure[key])
            elif issubclass(value_type, Model):
                converted_value = self.deserialize_model(field_name, value, structure[key])
            else:
                converted_value = TypeUtil.cast(value, value_type)
                if type(converted_value) != value_type:
                    raise InvalidValueException(
                        "Type mismatch for field '%s'. Value type '%s' does not match with defined type '%s'" % (
                            key, type(value_type), value_type))

            return_dict[key] = converted_value
        return return_dict

    def deserialize_model(self, field_name, value_obj, value_type):
        logging.debug("Deserializing model")
        if value_obj is None or value_type is None: return

        if issubclass(value_type, Model):
            if value_type == Model: return
            return value_type().from_dict_deep(value_obj)
        else:
            return value_obj

            # def _include_obj(self, obj_dict: dict, field_name: str):
            #     value_obj = getattr(self, field_name, None)
            #     if value_obj and isinstance(value_obj, Model):
            #         obj_dict[field_name] = value_obj.to_dict_deep()
            #     else:
            #         obj_dict[field_name] = value_obj
            #
            #         # def _exclude_obj(self, obj_dict: dict, name: str):
            #         #     if not obj_dict or name not in obj_dict: return
            #         #     obj = obj_dict[name]
            #         #     field_name = name + "_id"
            #         #     if "id" in obj and field_name in self.__class__._structure: setattr(self, field_name, obj["id"])
            #
            # def _include_obj_list(self, obj_dict: dict, name: str):
            #     output_obj_list = []
            #     obj_list = getattr(self, name, None)
            #     if obj_list and isinstance(obj_list, list):
            #         for obj in obj_list:
            #             if isinstance(obj, Model):
            #                 output_obj_list.append(obj.to_dict_deep())
            #             else:
            #                 output_obj_list.append(obj)
            #
            #     if output_obj_list:
            #         obj_dict[name] = output_obj_list
            #
            # def _include_obj_list(self, obj_dict: dict, include: list, name: str):
            #     output_obj_list = []
            #     obj_list = getattr(self, name, None) if include and name in include else None
            #     if obj_list and isinstance(obj_list, list):
            #         for obj in obj_list:
            #             if isinstance(obj, DictSerializable):
            #                 output_obj_list.append(obj.to_dict_deep())
            #             else:
            #                 output_obj_list.append(obj)
            #     if output_obj_list:
            #       obj_dict[name] = output_obj_list
