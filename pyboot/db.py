from enum import Enum

from sqlalchemy import Column, Integer, inspect, String, Float, Boolean, DateTime, Date, and_, or_
from sqlalchemy import distinct
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import RelationshipProperty, Query, Session

from pyboot.model import Model, TYPE_STR, TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_DATETIME, TYPE_DATE, TYPE_OBJ, TYPE_UNKNOWN, TYPE_LIST
from pyboot.page import Page


class FilterOperationEnum(Enum):
    IN = "in"
    EQUAL = "equal"
    RANGE = "range"


class FilterOperation(object):
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
        super().from_dict(obj_dict)
        return self

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
    def get_all(cls, db: Session, filters: dict = None, start: int = 0, count: int = 25, order_by=None, include: list = None) -> list:
        query = cls._get_all_query(db, filters=filters, include=include)
        query = cls._query(query, start=start, count=count + 1, order_by=order_by)
        return query.all()

    @classmethod
    def get_first(cls, db: Session, filters: dict = None, start: int = 0, order_by=None, include: list = None) -> list:
        query = cls._get_all_query(db, filters=filters, include=include)
        query = cls._query(query, start=start, count=1, order_by=order_by)
        return query.first()

    @classmethod
    def _get_all_query(cls, db: Session, filters: dict = None, include: list = None):
        columns = inspect(cls).columns
        query = db.query(cls)
        query = cls.join_tables(query, include)
        query = cls._generate_filter_query(query, filters, columns)
        return query

    @classmethod
    def get_page(cls, db: Session, filters: dict = None, start: int = 0, count: int = 25, order_by=None, include: list = None) -> list:
        page = Page()
        query = cls._get_all_query(db, filters=filters, include=include)
        page.items = cls._query(query, start=start, count=count + 1, order_by=order_by).all()
        page.total_count = query.count()
        page.gen_page_data(start, count)
        return page

    @classmethod
    def dump_detail_page(cls, db, fields, filters, start=0, count=1000):
        page = Page()
        columns = inspect(cls).columns
        query = db.query().add_column(distinct(cls.id))
        for field in fields:
            query = query.add_column(field)
        query = cls._generate_filter_query(query, filters, columns)
        result_rows = cls._query(query, start=start, count=count + 1).all()
        page.total_count = query.count()
        items = []
        for result in result_rows:
            item = dict()
            item["id"] = result[0]
            count = 1
            for field in fields:
                item[field.key] = result[count]
                count += 1
            items.append(item)
        page.items = items
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