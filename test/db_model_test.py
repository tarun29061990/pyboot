import sys, os

sys.path.insert(0, os.path.abspath("../"))

from unittest import TestCase

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
    def testRelationship(self):
        client = Client()
        client.id = 10
        client.name = "Rajeev"
        client.person_id = 1
        client.person = Person()
        client.person.id = 1
        client.person.name = "Sharma"
        print(client.to_dict_deep())
