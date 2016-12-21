import sys, os

sys.path.insert(0, os.path.abspath("../"))

import datetime
from pyboot.model import Model

from unittest import TestCase

from pyboot.util import ClassUtil


class Employee(Model):
    _structure = {
        "id": int,
        "name": str,
        "start_date": datetime.date
    }

    def __init__(self, id=None, name=None, start_date=None):
        self.id = id
        self.name = name
        self.start_date = start_date


class ClassUtilTest(TestCase):
    def test_get_class(self):
        obj = None
        try:
            klass = ClassUtil.get_class_by_name("Employee")
        except Exception as e:
            print("Error in loading model %s" % str(e))
            return

        print(klass())
