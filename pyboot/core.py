class JSONSerializable(object):
    def to_json_dict(self, include: list = None) -> dict:
        return {}

    def from_json_dict(self, json_dict: dict):
        return self
