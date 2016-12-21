import sys, os

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
