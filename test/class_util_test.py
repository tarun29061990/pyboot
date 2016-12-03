import sys, os

sys.path.insert(0, os.path.abspath("../"))

from pyboot.model import Model
from unittest import TestCase

from pyboot.util import ClassUtil


class ClassUtilTest(TestCase):
    def test_get_class(self):
        # print(sys.path)
        obj = None
        try:
            klass = ClassUtil.get_class_by_name("pyboot.model.Model")
        except Exception as e:
            print("Error in loading model %s" % str(e))
            return

        print(klass())
