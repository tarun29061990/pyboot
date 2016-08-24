from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import Session

from pyboot.util import Parser, DateTimeUtil, Validator, DateUtil
from pyboot.json import JSONSerializable

TYPE_INT = "int"
TYPE_FLOAT = "float"
TYPE_BOOL = "bool"
TYPE_STR = "str"
TYPE_DATETIME = "datetime"
TYPE_DATE = "date"
TYPE_ENUM = "enum"
TYPE_LIST = "list"
TYPE_OBJ = "obj"
TYPE_UNKNOWN = "unknown"


class Model(JSONSerializable):
    _fields = None

    @classmethod
    def _get_fields(cls):
        return cls._fields

    def _to_dict_field(self, obj_dict, name: str, type: str = None):
        if not name or name not in self.__dict__: return
        value = getattr(self, name)
        if type == TYPE_STR:
            obj_dict[name] = Parser.str(value)
        elif type == TYPE_INT:
            obj_dict[name] = Parser.int(value)
        elif type == TYPE_FLOAT:
            obj_dict[name] = Parser.float(value)
        elif type == TYPE_BOOL:
            obj_dict[name] = Parser.bool(value)
        elif type == TYPE_DATETIME:
            if isinstance(value, str):
                obj_dict[name] = DateTimeUtil.iso_to_dt_local(value)
            else:
                obj_dict[name] = Validator.datetime(value)
        elif type == TYPE_DATE:
            if isinstance(value, str):
                obj_dict[name] = DateUtil.iso_to_date(value)
            else:
                obj_dict[name] = Validator.date(value)
        elif type == TYPE_OBJ:
            if isinstance(value, Model):
                obj_dict[name] = value.to_json_dict()
            else:
                obj_dict[name] = value
        elif type == TYPE_LIST:
            for value_item in value:
                if isinstance(value_item, Model):
                    obj_dict[name] = value_item.to_json_dict()
                else:
                    obj_dict[name] = value_item
        elif type == TYPE_UNKNOWN:
            obj_dict[name] = value
        else:
            obj_dict[name] = value

    def _from_dict_field(self, obj_dict: dict, name: str, type: str = None):
        if not name or not obj_dict or name not in obj_dict: return
        value = obj_dict.get(name)
        if type == TYPE_STR:
            setattr(self, name, Parser.str(value))
        elif type == TYPE_INT:
            setattr(self, name, Parser.int(value))
        elif type == TYPE_FLOAT:
            setattr(self, name, Parser.float(value))
        elif type == TYPE_BOOL:
            setattr(self, name, Parser.bool(value))
        elif type == TYPE_DATETIME:
            if isinstance(value, str):
                setattr(self, name, DateTimeUtil.iso_to_dt_local(value))
            else:
                setattr(self, name, Validator.datetime(value))
        elif type == TYPE_DATE:
            if isinstance(value, str):
                setattr(self, name, DateUtil.iso_to_date(value))
            else:
                setattr(self, name, Validator.date(value))
        elif type == TYPE_OBJ:
            if isinstance(value, Model):
                setattr(self, name, value.from_json_dict())
            else:
                setattr(self, name, value)
        elif type == TYPE_LIST:
            for value_item in value:
                if isinstance(value_item, Model):
                    setattr(self, name, value_item.to_json_dict())
                else:
                    setattr(self, name, value_item)
        elif type == TYPE_UNKNOWN:
            setattr(self, name, value)
        else:
            setattr(self, name, value)

    def to_dict(self):
        obj_dict = {}
        if self.id: obj_dict["id"] = self.id

        fields = self.__class__._get_fields()
        if not fields: return obj_dict
        for field_name in fields.keys():
            self._to_dict_field(obj_dict, field_name, fields[field_name])

        return obj_dict

    def from_dict(self, obj_dict: dict):
        if not obj_dict: return
        if "id" in obj_dict: self.id = obj_dict["id"]

        fields = self.__class__._get_fields()
        if not fields: return self
        for field_name in fields:
            self._from_dict_field(obj_dict, field_name, fields[field_name])

        return self

    def to_json_dict(self, include: list = None) -> dict:
        json_dict = self.to_dict()

        fields = self.__class__._get_fields()
        if not fields: return json_dict
        for field_name in fields.keys():
            if fields[field_name] == TYPE_OBJ:
                self._include_obj(json_dict, include, field_name)
        return json_dict

    def from_json_dict(self, json_dict: dict):
        self.from_dict(json_dict)

        fields = self.__class__._get_fields()
        if not fields: return self
        for field_name in fields:
            if fields[field_name] == TYPE_OBJ:
                self._exclude_obj(json_dict, field_name)
        return self

    def _include_obj(self, json_dict: dict, include: list, name: str):
        if not include: include = []
        field_name = name + "_id"

        sub_obj = getattr(self, name, None) if name in include else None
        value = getattr(self, field_name, None)
        if sub_obj:
            if isinstance(sub_obj, Model): json_dict[name] = sub_obj.to_dict()
        elif value:
            json_dict[name] = {"id": value}
        elif name in include:
            json_dict[name] = None

        if field_name in json_dict: del json_dict[field_name]

    def _exclude_obj(self, json_dict: dict, name: str):
        if not json_dict: return
        if name in json_dict and "id" in json_dict[name]:
            setattr(self, name + "_id", json_dict[name]["id"])


class DatabaseModel(Model):
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)  # type: int

    @classmethod
    def _get_fields(cls):
        if cls._fields: return cls._fields

        columns = inspect(cls).columns
        if not columns: return None
        cls._fields = {}
        for column in columns:
            type = column.type
            if isinstance(type, String):
                cls._fields[column.key] = TYPE_STR
            elif isinstance(type, Integer):
                cls._fields[column.key] = TYPE_INT
            elif isinstance(type, Float):
                cls._fields[column.key] = TYPE_FLOAT
            elif isinstance(type, Boolean):
                cls._fields[column.key] = TYPE_BOOL
            elif isinstance(type, DateTime):
                cls._fields[column.key] = TYPE_DATETIME
            elif isinstance(type, Date):
                cls._fields[column.key] = TYPE_DATE
            elif isinstance(type, RelationshipProperty):
                cls._fields[column.key] = TYPE_OBJ
            else:
                cls._fields[column.key] = TYPE_UNKNOWN

        relationships = inspect(cls).relationships
        for relation in relationships:
            if relation.uselist:
                cls._fields[relation.key] = TYPE_LIST
            else:
                cls._fields[relation.key] = TYPE_OBJ

                # if relation.direction.name == "ONETOMANY" or relation.direction.name == "MANYTOMANY":
                #     cls._fields[relation.key] = TYPE_LIST
                # elif relation.direction.name == "ONETOONE" or relation.direction.name == "MANYTOONE":
                #     cls._fields[relation.key] = TYPE_OBJ
                # else:
                #     cls._fields[relation.key] = TYPE_UNKNOWN

        return cls._fields

    @classmethod
    def _query(cls, query: Query, start: int = None, count: int = None, order_by=None) -> Query:
        if start: query = query.offset(start)
        if count: query = query.limit(count)
        if order_by is not None: query = query.order_by(order_by)
        return query

    @classmethod
    def get_all(cls, db: Session, start: int = None, count: int = None, order_by=None, include: list = None) -> list:
        query = cls._query(db.query(cls), start=start, count=count, order_by=order_by)
        cls.join_tables(query, include)
        return query.all()

    @classmethod
    def get(cls, db: Session, id: int, include: list = None):
        query = db.query(cls)  # type: Query
        query = cls.join_tables(query, include)
        return query.get(id)

    @classmethod
    def delete(cls, db: Session, id: int):
        db.query(cls).filter(cls.id == id).delete()

    @classmethod
    def join_tables(cls, query: Query, include: list = None) -> Query:
        return query


DBModelBase = declarative_base(cls=DatabaseModel)
