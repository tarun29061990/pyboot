from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from pyboot.model import DatabaseModelBase


class Client(DatabaseModelBase):
    __tablename__ = "clients"

    name = Column(String)
    person_id = Column(Integer, ForeignKey("person.id"))


class Person(DatabaseModelBase):
    __tablename__ = "persons"

    name = Column(String)

    clients = relationship(Client)


if __name__ == "__main__":
    person = Person()
    print(person.to_json_dict())
