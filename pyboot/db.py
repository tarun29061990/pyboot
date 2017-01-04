from enum import Enum

import datetime

from sqlalchemy import Column, Integer, inspect, String, Float, Boolean, DateTime, Date, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import RelationshipProperty, Query, Session

from pyboot.model import Model
from pyboot.page import Page


class FilterOperationEnum(Enum):
    IN = "in"
    EQUAL = "equal"
    RANGE = "range"


class FilterOperation:
    def __init__(self, operation: FilterOperationEnum, column: str, value):
        self.operation = operation.value
        self.column = column
        self.value = value

    def db_filter(self):
        return {
            "op": self.operation,
            "column": self.column,
            "value": self.value
        }


class DatabaseModel(Model):
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)  # type: int

    def __init__(self):
        self.__obj_always = False

    @classmethod
    def _get_structure(cls):
        if cls._structure: return cls._structure

        columns = inspect(cls).columns
        if not columns: return None
        cls._structure = {}
        for column in columns:
            type = column.type
            if isinstance(type, String):
                cls._structure[column.key] = str
            elif isinstance(type, Integer):
                cls._structure[column.key] = int
            elif isinstance(type, Float):
                cls._structure[column.key] = float
            elif isinstance(type, Boolean):
                cls._structure[column.key] = bool
            elif isinstance(type, DateTime):
                cls._structure[column.key] = datetime.datetime
            elif isinstance(type, Date):
                cls._structure[column.key] = datetime.date
            elif isinstance(type, RelationshipProperty):
                cls._structure[column.key] = Model
            else:
                cls._structure[column.key] = None

        relationships = inspect(cls).relationships
        for relation in relationships:
            if relation.uselist:
                cls._structure[relation.key] = list
            else:
                cls._structure[relation.key] = Model

        return cls._structure

    def to_dict(self):
        obj_dict = super().to_dict()
        if self.id: obj_dict["id"] = self.id
        return obj_dict

    def from_dict(self, obj_dict: dict):
        if not obj_dict: return
        if "id" in obj_dict: self.id = obj_dict["id"]
        super().from_dict(obj_dict)
        return self

    def to_dict_deep(self, obj_always: bool = False) -> dict:
        self.__obj_always = obj_always
        return super().to_dict_deep()

        # if not obj_always:
        #     return super().to_dict_deep()
        #
        # obj_dict = self.to_dict()
        # structure = self.__class__._get_structure()
        # if not structure: return obj_dict
        # for field_name in structure.keys():
        #     obj_type = structure[field_name]
        #     if issubclass(obj_type, Model):
        #         self._include_obj(obj_dict, field_name)
        #     elif obj_type is list:
        #         self._include_obj_list(obj_dict, field_name)
        # return obj_dict

    def from_dict_deep(self, obj_dict: dict, obj_always: bool = False):
        self.__obj_always = obj_always
        return super().from_dict_deep(obj_dict)

        # if not obj_always:
        #     return super().from_dict_deep(obj_dict)
        #
        # self.from_dict(obj_dict)
        # structure = self.__class__._get_structure()
        # if not structure: return self
        # for field_name in structure:
        #     obj_type = structure[field_name]
        #     if issubclass(obj_type, Model):
        #         self._exclude_obj(obj_dict, field_name)
        # return self

    # def _include_obj_list(self, obj_dict: dict, name: str):
    #     if not self.__obj_always:
    #         return super()._include_obj_list(obj_dict, name)
    #
    #     json_list = []
    #     obj_list = getattr(self, name, None)
    #     if obj_list and isinstance(obj_list, list):
    #         for obj in obj_list:
    #             if isinstance(obj, Model):
    #                 json_list.append(obj.to_dict_deep())
    #             else:
    #                 json_list.append(obj)
    #     obj_dict[name] = json_list

    # def _include_obj(self, obj_dict: dict, name: str):
    #     if not self.__obj_always:
    #         return super()._include_obj(obj_dict, name)
    #
    #     field_name = name + "_id"
    #
    #     sub_obj = getattr(self, name, None)
    #     value = getattr(self, field_name, None) if field_name in self.__dict__ else None
    #     if sub_obj:
    #         if isinstance(sub_obj, Model): obj_dict[name] = sub_obj.to_dict_deep()
    #     elif value:
    #         obj_dict[name] = {"id": value}
    #
    #     if field_name in obj_dict: del obj_dict[field_name]
    #
    # def _exclude_obj(self, obj_dict: dict, name: str):
    #     # if not self.obj_always:
    #     #     return super()._exclude_obj(obj_dict, name)
    #
    #     if not obj_dict or name not in obj_dict: return
    #     obj = obj_dict[name]
    #     field_name = name + "_id"
    #     if "id" in obj and field_name in self.__class__._structure: setattr(self, field_name, obj["id"])

    @classmethod
    def _query(cls, query: Query, start: int = None, count: int = None, order_by=None) -> Query:
        if order_by is not None:
            order_by_query = []
            columns = inspect(cls).columns
            for order_by_element in order_by:
                for key in order_by_element:
                    if key not in columns: continue
                    if order_by_element[key] == "asc":
                        order_by_query.append(columns[key].asc())
                    else:
                        order_by_query.append(columns[key].desc())
            query = query.order_by(*order_by_query)
        if start: query = query.offset(start)
        if count: query = query.limit(count)
        return query

    @classmethod
    def get_all(cls, session: Session, filters: dict = None, start: int = 0, count: int = 25, order_by=None,
                include: list = None) -> list:
        query = cls._get_all_query(session, filters=filters, include=include)
        query = cls._query(query, start=start, count=count + 1, order_by=order_by)
        return query.all()

    @classmethod
    def _get_all_query(cls, session: Session, filters: dict = None, include: list = None):
        columns = inspect(cls).columns
        query = session.query(cls)
        query = cls.join_tables(query, include)
        query = cls._generate_filter_query(query, filters, columns)
        return query

    @classmethod
    def get_page(cls, session: Session, filters: dict = None, start: int = 0, count: int = 25, order_by=None,
                 include: list = None) -> Page:
        page = Page()
        query = cls._get_all_query(session, filters=filters, include=include)
        page.items = cls._query(query, start=start, count=count + 1, order_by=order_by).all()
        page.total_count = query.count()
        page.gen_page_data(start, count)
        return page

    @classmethod
    def _generate_filter_query(cls, query, filters: dict, columns):
        if not filters or not isinstance(filters, list):
            return query
        or_filters_list = []
        and_filters_list = []
        for and_filter in filters:
            if "or" in and_filter and and_filter["or"] and isinstance(and_filter["or"], list):
                for or_filter in and_filter["or"]:
                    or_operation = cls.__get_operation_query(or_filter, columns)
                    if or_operation is None: continue
                    if isinstance(or_operation, list):
                        or_filters_list.extend(or_operation)
                    else:
                        or_filters_list.append(or_operation)
            else:
                and_operation = cls.__get_operation_query(and_filter, columns)
                if and_operation is None:
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
        if not input_filter:
            return
        operation = input_filter["op"] if "op" in input_filter else None
        column_name = input_filter["column"] if "column" in input_filter else None
        value = input_filter["value"] if "value" in input_filter else None
        if column_name not in columns: return
        if not operation or not column_name or value is None:
            return
        if operation == FilterOperationEnum.IN.value:
            return columns[column_name].in_(value)
        if operation == FilterOperationEnum.EQUAL.value:
            return columns[column_name] == value
        if operation == FilterOperationEnum.RANGE.value:
            range_query = []
            if isinstance(value, list):
                if len(value) == 1 or len(value) == 2 and value[0]:
                    range_query.append(columns[column_name] > value[0])
                else:
                    range_query.append(columns[column_name] < value[1])
                return range_query

    @classmethod
    def get(cls, session: Session, id: int, include: list = None):
        query = session.query(cls)  # type: Query
        query = cls.join_tables(query, include)
        return query.get(id)

    @classmethod
    def delete(cls, session: Session, id: int):
        session.query(cls).filter(cls.id == id).delete()

    @classmethod
    def join_tables(cls, query: Query, include: list = None) -> Query:
        return query


DBModelBase = declarative_base(cls=DatabaseModel)
