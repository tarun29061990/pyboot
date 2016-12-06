from pyboot.core import DictSerializable
from pyboot.util import TypeUtil


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

    def _to_dict_field(self, obj_dict, name: str, value_type=None):
        if not name or name not in self.__dict__:
            return

        if type(value_type) is type:
            obj_dict[name] = TypeUtil.cast(getattr(self, name), value_type)

    def _from_dict_field(self, obj_dict: dict, name: str, value_type=None):
        if not name or not obj_dict or name not in obj_dict:
            return

        if type(value_type) is type:
            setattr(self, name, TypeUtil.cast(obj_dict.get(name), value_type))

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

    def to_dict_deep(self) -> dict:
        obj_dict = self.to_dict()

        structure = self.__class__._get_structure()
        if not structure: return obj_dict
        for field_name in structure.keys():
            obj_type = structure[field_name]
            if type(obj_type) is list:
                # This needs to handle list of all types (primitives, object etc)
                self._include_obj_list(obj_dict, field_name)
            if type(obj_type) is dict:
                # This needs to handle object of all types (primitives, object etc)
                self._include_obj(obj_dict, field_name)
            elif type(obj_type) is type:
                if issubclass(obj_type, Model):
                    self._include_obj(obj_dict, field_name)
        return obj_dict

    def from_dict_deep(self, obj_dict: dict):
        self.from_dict(obj_dict)

        structure = self.__class__._get_structure()
        if not structure: return self

        # for field_name in structure:
        #     obj_type = structure[field_name]
        #     if issubclass(obj_type, object):
        #         self._exclude_obj(obj_dict, field_name)
        # return self

    def _include_obj(self, obj_dict: dict, name: str):
        sub_obj = getattr(self, name, None)
        if sub_obj and isinstance(sub_obj, Model):
            obj_dict[name] = sub_obj.to_dict_deep()

            # def _exclude_obj(self, obj_dict: dict, name: str):
            #     if not obj_dict or name not in obj_dict: return
            #     obj = obj_dict[name]
            #     field_name = name + "_id"
            #     if "id" in obj and field_name in self.__class__._structure: setattr(self, field_name, obj["id"])

    def _include_obj_list(self, obj_dict: dict, name: str):
        output_obj_list = []
        obj_list = getattr(self, name, None)
        if obj_list and isinstance(obj_list, list):
            for obj in obj_list:
                if isinstance(obj, Model):
                    output_obj_list.append(obj.to_dict_deep())
                else:
                    output_obj_list.append(obj)

        if output_obj_list:
            obj_dict[name] = output_obj_list

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
