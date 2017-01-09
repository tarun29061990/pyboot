import datetime
import sys, os

from sqlalchemy import DateTime

sys.path.insert(0, os.path.abspath("../"))

from unittest import TestCase
from pyboot.json import load_json
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from pyboot.db import DBModelBase


class Person(DBModelBase):
    __tablename__ = "persons"

    name = Column(String)


class Client(DBModelBase):
    __tablename__ = "clients"

    name = Column(String)
    person_id = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person)


class City(DBModelBase):
    __tablename__ = "cities"

    code = Column(String(64), nullable=False)
    display_name = Column(String(64), nullable=False)
    state_id = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    created_by_id = Column(Integer, nullable=False)
    updated_by_id = Column(Integer, nullable=False)


class ModelTest(TestCase):
    def test_to_dict_deep(self):
        client = Client()
        client.id = 10
        client.name = "Rajeev"
        client.person_id = 1

        person = Person()
        person.id = 1
        person.name = "Sharma"

        client.person = person
        print(client.to_dict_deep())

    def test_from_dict_deep(self):
        obj_dict = load_json('{"person_id": 1, "name": "Rajeev", "id": 10, "person": {"name": "Sharma", "id": 1}}')

        client = Client().from_dict_deep(obj_dict)

        print(client.to_dict_deep())
