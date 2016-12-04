import sys, os

sys.path.insert(0, os.path.abspath("../"))

from pyboot.model import Model
from unittest import TestCase


class Person(Model):
    _structure = {
        "id": int,
        "name": str
    }


class Client(Model):
    _structure = {
        "id": int,
        "name": str,
        "person": Person
    }


class ModelTest(TestCase):
    def testRelationship(self):
        client = Client()
        client.name = "Rajeev"
        client.person = Person()
        client.person.id = 1
        client.person.name = "Sharma"
        print(client.to_json_dict())
