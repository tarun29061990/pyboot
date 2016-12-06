class DictSerializable(object):
    def to_dict(self) -> dict:
        return {}

    def from_dict(self, obj_dict: dict):
        return self

    def to_dict_deep(self) -> dict:
        return {}

    def from_dict_deep(self, obj_dict: dict):
        return self
