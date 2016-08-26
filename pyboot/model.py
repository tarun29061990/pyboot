from pyboot.page import Page
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import and_
from sqlalchemy import inspect
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import Session

from pyboot.util import Parser, DateTimeUtil, Validator, DateUtil

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


class JSONSerializable(object):
    def to_json_dict(self, include: list = None) -> dict:
        return {}

    def from_json_dict(self, json_dict: dict):
        return self


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
        elif type == TYPE_UNKNOWN:
            setattr(self, name, value)
        else:
            setattr(self, name, value)

    def to_dict(self):
        obj_dict = {}
        fields = self.__class__._get_fields()
        if not fields: return obj_dict
        for field_name in fields.keys():
            self._to_dict_field(obj_dict, field_name, fields[field_name])
        return obj_dict

    def from_dict(self, obj_dict: dict):
        if not obj_dict: return

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
            type = fields[field_name]
            if type == TYPE_OBJ:
                self._include_obj(json_dict, include, field_name)
            elif type == TYPE_LIST:
                self._include_obj_list(json_dict, include, field_name)
        return json_dict

    def from_json_dict(self, json_dict: dict):
        self.from_dict(json_dict)

        fields = self.__class__._get_fields()
        if not fields: return self
        for field_name in fields:
            type = fields[field_name]
            if type == TYPE_OBJ:
                self._exclude_obj(json_dict, field_name)
        return self

    def _include_obj_list(self, json_dict: dict, include: list, name: str):
        json_list = []
        obj_list = getattr(self, name, None) if name in include else None
        if obj_list and isinstance(obj_list, list):
            for obj in obj_list:
                if isinstance(obj, JSONSerializable):
                    obj_list.append(obj.to_json_dict())
                else:
                    obj_list.append(obj)
        json_dict[name] = json_list

    def _include_obj(self, json_dict: dict, include: list, name: str):
        if not include: include = []
        field_name = name + "_id"

        sub_obj = getattr(self, name, None) if name in include else None
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
        if "id" in obj and field_name in self.__class__._fields: setattr(self, field_name, obj["id"])


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

        return cls._fields

    def to_dict(self):
        obj_dict = super().to_dict()
        if self.id: obj_dict["id"] = self.id
        return obj_dict

    def from_dict(self, obj_dict: dict):
        if not obj_dict: return
        if "id" in obj_dict: self.id = obj_dict["id"]
        super().to_dict()
        return self

    @classmethod
    def _query(cls, query: Query, start: int = None, count: int = None, order_by=None) -> Query:
        if start: query = query.offset(start)
        if count: query = query.limit(count)
        if order_by is not None: query = query.order_by(order_by)
        return query

    # filters= [
    #     {"or": [
    #         {op:"in", column:'column', value:'value'}},
    #         {op:"equal", column:'column', value:'value'}},
    #         {op:"range", column:'column', value:['start_value', 'end_value']}},
    #         {op:"ilike", column:'column', value:'value'}}
    #     ]},
    #     {op:"in", column:'column', value:'value'}},
    #     {op:"equal", column:'column', value:'value'}},
    #     {op:"range", column:'column', value:['start_value', 'end_value']}},
    #     {op:"ilike", column:'column', value:'value'}}
    # ]

    @classmethod
    def get_all(cls, db: Session, filters: dict=None, start: int = 0, count: int = 25, order_by=None, include: list = None) -> list:
        columns = inspect(cls).columns
        query = db.query(cls)
        cls.join_tables(query, include)
        query = cls.generate_filter_query(query, filters, columns)
        query = cls._query(query, start=start, count=count, order_by=order_by)
        return query.all()

    @classmethod
    def get_page(cls, db: Session, filters: dict=None, start: int = 0, count: int = 25, order_by=None, include: list = None) -> list:
        page = Page()
        columns = inspect(cls).columns
        query = db.query(cls)
        cls.join_tables(query, include)
        query = cls.generate_filter_query(query, filters, columns)
        page.items = cls._query(query, start=start, count=count, order_by=order_by).all()
        page.total_count = query.count()
        page.gen_page_data(start, count)
        return page

    @classmethod
    def _generate_filter_query(cls, query, filters: dict, columns):
        if not filters or isinstance(filters, list):
            return query
        or_filters_list = []
        and_filters_list = []
        for and_filter in filters:
            if "or" in and_filter and and_filter["or"] and isinstance(and_filter["or"], list):
                for or_filter in and_filter["or"]:
                    or_operation = cls.__get_operation_query(or_filter, columns)
                    if not query: continue
                    if isinstance(or_operation, list):
                        or_filters_list.extend(or_operation)
                    else:
                        or_filters_list.append(or_operation)
            else:
                and_operation = cls.__get_operation_query(and_filter, columns)
                if not and_operation:
                    continue
                if isinstance(and_operation, list):
                    and_filters_list.extend(and_operation)
                else:
                    and_filters_list.append(and_operation)
        if and_filters_list and len(and_filters_list) > 0:
            query = query.filter(and_(*and_filters_list))
        if or_filters_list and len(or_filters_list) > 0:
            query = query.filter(or_(*or_filters_list))
        return query

    @classmethod
    def __get_operation_query(cls, input_filter, columns):
        # filters_list = []
        if input_filter:
            return
        operation = input_filter["op"] if "op" in input_filter else None
        column_name = input_filter["column"] if "column" in input_filter else None
        value = input_filter["value"] if "value" in input_filter else None

        if not operation or not column_name or not value:
            return
        if operation == "in":
            return columns[column_name].in_(value)
        if operation == "equal":
            return columns[column_name] == value
        if operation == "range":
            range_query = []
            if isinstance(value, list):
                if len(value) == 1 or len(value) == 2 and value[0]:
                    range_query.append(columns[column_name] > value[0])
                else:
                    range_query.append(columns[column_name] < value[1])
                return range_query

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
