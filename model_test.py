from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from pyboot.db import DBModelBase


class Client(DBModelBase):
    __tablename__ = "clients"

    name = Column(String)
    person_id = Column(Integer, ForeignKey("persons.id"))


class Person(DBModelBase):
    __tablename__ = "persons"

    name = Column(String)

    clients = relationship(Client, uselist=False)


if __name__ == "__main__":
    person = Person()
    print(person.to_json_dict())
