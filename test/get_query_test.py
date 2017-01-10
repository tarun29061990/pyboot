import sys, os

from pyboot.db import FilterOperation, FilterOperationEnum

sys.path.insert(0, os.path.abspath("../"))

import datetime
from pyboot.model import Model
from pyboot.json import dump_json, load_json
from unittest import TestCase


class Employee(Model):
    def get_all(self):
        filter_query = []
        filter_query.append(FilterOperation(FilterOperationEnum.IN, "id", [1, 5,10,12]).db_filter())
        filter_query.append(FilterOperation(FilterOperationEnum.EQUAL, "name", "TestName").db_filter())
        # or query
        filter_or_query = []
        filter_or_query.append(FilterOperation(FilterOperationEnum.IN, "user_id", [1, 5,10,12]).db_filter())
        filter_or_query.append(FilterOperation(FilterOperationEnum.IN, "customer_id", [1, 5,10,12]).db_filter())
        filter_query.append({"or": filter_or_query})



class Company(Model):
    _structure = {
        "id": int,
        "name": str,
        "start_date": datetime.date,
        "manager_id": int,
        "manager": "json_model_test.Employee",
        "all_employees": [Employee],
        "ceo_details": {
            "ceo": Employee,
            "start_date": datetime.date,
            "key1": {
                "key2": Employee
            }
        }
    }


class ModelTest(TestCase):
    def test_to_dict_deep(self):
        company = Company()
        company.id = 10
        company.name = "Livspace"
        company.start_date = "2013-04-28"

        company.manager_id = 1

        rajeev = Employee(1, "Rajeev Sharma", "2013-04-29")
        vidur = Employee(2, "Vidur Jain", "2015-01-01")

        company.manager = rajeev
        company.all_employees = [rajeev, vidur]

        company.ceo_details = {
            "ceo": Employee(3, "Anuj Srivastava", "2014-01-01"),
            "start_date": "2014-01-01",
            "key1": {
                "key2": Employee(4, "Anuj Srivastava", "2014-01-01")
            }
        }

        print(dump_json(company.to_dict_deep()))

    def test_from_dict_deep(self):
        obj_dict = load_json(
            '{"manager_id": 1, "start_date": "2013-04-28", "id": 10, "all_employees": [{"start_date": "2013-04-29", "name": "Rajeev Sharma", "id": 1}, {"start_date": "2015-01-01", "name": "Vidur Jain", "id": 2}], "manager": {"start_date": "2013-04-29", "name": "Rajeev Sharma", "id": 1}, "ceo_details": {"key1": {"key2": {"start_date": "2014-01-01", "name": "Anuj Srivastava", "id": 4}}, "start_date": "2014-01-01", "ceo": {"start_date": "2014-01-01", "name": "Anuj Srivastava", "id": 3}}}')

        company = Company()
        company.from_dict_deep(obj_dict)

        print(company)
