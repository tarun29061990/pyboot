import datetime
import os
import random
import tempfile

import iso8601
import pytz
import tzlocal

from pyboot.common.exception import InvalidValueException


class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


class FileUtil(object):
    @staticmethod
    def get_ext_with_dot(file):
        return os.path.splitext(file)[1]

    @staticmethod
    def get_ext(file):
        return os.path.splitext(file)[1][1:]

    @staticmethod
    def save_flask_file_to_temp_from_req(filename, flask_files):
        if filename in flask_files and flask_files[filename].filename:
            uploaded_file = flask_files[filename]
            temp_file = "/tmp/" + next(tempfile._get_candidate_names()) + FileUtil.get_ext_with_dot(
                uploaded_file.filename)
            uploaded_file.save(temp_file)
            return temp_file

    @staticmethod
    def save_flask_file_to_temp(flask_file):
        if flask_file and flask_file.filename:
            temp_file = "/tmp/" + next(tempfile._get_candidate_names()) + FileUtil.get_ext_with_dot(flask_file.filename)
            flask_file.save(temp_file)
            return temp_file, flask_file.filename

    @staticmethod
    def gen_random_filename(filename):
        return str(int(datetime.time() * 1000000)) + str(random.randint(10000, 99999)) + FileUtil.get_ext_with_dot(
            filename)


class DateUtil(object):
    @staticmethod
    def date_to_iso(date):
        if date is None: return
        return date.isoformat()

    @staticmethod
    def iso_to_date(date_str):
        return iso8601.parse_date(date_str)


class TimeUtil(object):
    @staticmethod
    def time_to_iso(time):
        if time is None: return
        return time.isoformat()


class DatetimeUtil(object):
    default_tz = tzlocal.get_localzone()

    @staticmethod
    def iso_to_dt_utc(dt_str, microseconds=False, default=None):
        if dt_str is None: return default
        dt = iso8601.parse_date(dt_str)
        dt = dt.astimezone(pytz.utc)
        if not microseconds:
            dt = dt.replace(microsecond=0)
        return dt

    @staticmethod
    def iso_to_dt_local(dt_str, microseconds=False, default=None):
        if dt_str is None: return default
        dt = iso8601.parse_date(dt_str)
        dt = dt.astimezone(tzlocal.get_localzone())
        if not microseconds:
            dt = dt.replace(microsecond=0)
        return dt

    @staticmethod
    def iso_to_dt_timezone(dt_str, timezone, microseconds=False, default=None):
        if dt_str is None: return default
        dt = iso8601.parse_date(dt_str)
        dt = dt.astimezone(timezone)
        if not microseconds:
            dt = dt.replace(microsecond=0)
        return dt

    @staticmethod
    def dt_to_iso(dt, default_tz=default_tz, microseconds=False, default=None):
        if dt is None: return default
        if dt.tzinfo is None:
            dt = default_tz.localize(dt)
        dt = dt.astimezone(pytz.utc)
        if not microseconds:
            dt = dt.replace(microsecond=0)
        return dt.isoformat()

    @staticmethod
    def dt_to_dt_local(dt, default_tz=default_tz, default=None):
        if dt is None: return default
        if dt.tzinfo is None:
            dt = default_tz.localize(dt)
        return dt.astimezone(tzlocal.get_localzone())

    @staticmethod
    def dt_to_dt_utc(dt, default_tz=default_tz, default=None):
        if dt is None: return default
        if dt.tzinfo is None:
            dt = default_tz.localize(dt)
        return dt.astimezone(pytz.utc)

    @staticmethod
    def dt_to_dt_timezone(dt, timezone, default_tz=default_tz, default=None):
        if dt is None: return default
        if dt.tzinfo is None:
            dt = default_tz.localize(dt)
        return dt.astimezone(timezone)

    @staticmethod
    def diff(start, end, microseconds=False):
        delta = (end - start).total_seconds()
        if not microseconds:
            delta *= 1000
        return int(delta)


class DictUtil(object):
    @staticmethod
    def clone(obj_dict):
        if obj_dict is None: return
        new_dict = {}
        for key in obj_dict:
            new_dict[key] = obj_dict[key]
        return new_dict

    @staticmethod
    def delete_keys(obj_dict, *args):
        if obj_dict is None: return
        for key in args:
            if key in obj_dict:
                del obj_dict[key]
        return obj_dict

    @staticmethod
    def delete_null_values(obj_dict):
        if obj_dict is None: return
        new_dict = {}
        for key in obj_dict:
            if obj_dict[key] is not None:
                new_dict[key] = obj_dict[key]
        return new_dict

    @staticmethod
    def join(obj_dict, key_sep="&", val_sep="="):
        if obj_dict is None: return
        join_str = ""
        for key in obj_dict:
            join_str += str(key) + str(val_sep) + str(obj_dict[key]) + str(key_sep)
        return join_str[:-1]


class Parser(object):
    @staticmethod
    def int(value, default=None):
        if value is None or value == "": return default
        try:
            return int(value)
        except:
            raise InvalidValueException("Invalid int value '%s'" % value)

    @staticmethod
    def float(value, default=None):
        if value is None or value == "": return default
        try:
            return float(value)
        except:
            raise InvalidValueException("Invalid float value '%s'" % value)

    @staticmethod
    def str(value, default=None):
        if value is None or value == "": return default
        return str(value)

    @staticmethod
    def str_title(value, default=None):
        if value is None or value == "": return default
        return str(value).title()

    @staticmethod
    def str_lower(value, default=None):
        if value is None or value == "": return default
        return str(value).lower()

    @staticmethod
    def str_upper(value, default=None):
        if value is None or value == "": return default
        return str(value).upper()

    @staticmethod
    def datetime(value_dt, default=None):
        if value_dt is None: return default
        if not isinstance(value_dt, datetime.datetime):
            raise InvalidValueException("Value is not datetime instance '%s'" % value_dt)
        return value_dt

    @staticmethod
    def date(value_date, default=None):
        if value_date is None: return default
        if not isinstance(value_date, datetime.date):
            raise InvalidValueException("Value is not date instance '%s'" % value_date)
        return value_date

    @staticmethod
    def time(value_time, default=None):
        if value_time is None: return default
        if not isinstance(value_time, datetime.time):
            raise InvalidValueException("Value is not time instance '%s'" % value_time)
        return value_time

    @staticmethod
    def bool(value, default=None):
        if value is None or value == "": return default
        if isinstance(value, bool): return value
        value = value.lower()
        if value == "yes" or value == "on" or value == "true":
            return True
        elif value == "no" or value == "off" or value == "false":
            return False
        else:
            raise InvalidValueException("Invalid bool value '%s'" % value)

    # @staticmethod
    # def str_to_date(date_str, format, default=None):
    #     if date_str is None or date_str == "":
    #         return default
    #
    #     try:
    #         return datetime.datetime.strptime(date_str, format)
    #     except:
    #         raise InvalidValueException("Invalid date format '%s'" % date_str)

    @staticmethod
    def list(value_dict, default=None):
        if value_dict is None: return default
        if not isinstance(value_dict, list):
            raise InvalidValueException("Value is not a list instance '%s'" % value_dict)
        return value_dict

    @staticmethod
    def dict(value_dict, default=None):
        if value_dict is None: return default
        if not isinstance(value_dict, dict):
            raise InvalidValueException("Value is not a dict instance '%s'" % value_dict)
        return value_dict

    @staticmethod
    def int_csv_to_list(value_csv, default=None):
        if value_csv is None or value_csv == "": return default
        values = [value.strip() for value in value_csv.split(",")]
        int_values = []
        for value in values:
            try:
                int_values.append(int(value))
            except:
                raise InvalidValueException("Invalid int value '%s'" % value)
        return int_values

    @staticmethod
    def int_list(value_list, default=None):
        if value_list is None: return default
        if not isinstance(value_list, list):
            raise InvalidValueException("Value is not a dict instance '%s'" % value_list)
        values = [value.strip() for value in value_list]
        int_values = []
        for value in values:
            try:
                int_values.append(int(value))
            except:
                raise InvalidValueException("Invalid int value '%s'" % value)
        return int_values

    @staticmethod
    def str_csv_to_list(value_str, default=None):
        if value_str is None or value_str == "": return default
        return [value.strip() for value in value_str.split(",")]

    @staticmethod
    def str_list(value_list, default=None):
        if value_list is None: return default
        if not isinstance(value_list, list):
            raise InvalidValueException("Value is not a dict instance '%s'" % value_list)
        return [value.strip() for value in value_list]

    @staticmethod
    def str_list_upper(value_list, default=None):
        if value_list is None: return default
        if not isinstance(value_list, list):
            raise InvalidValueException("Value is not a dict instance '%s'" % value_list)
        return [value.strip().upper() for value in value_list]

    @staticmethod
    def str_list_lower(value_list, default=None):
        if value_list is None: return default
        if not isinstance(value_list, list):
            raise InvalidValueException("Value is not a dict instance '%s'" % value_list)
        return [value.strip().lower() for value in value_list]


class Validator:
    @staticmethod
    def datetime(value_dt, default=None):
        if value_dt is None:
            return default
        if not isinstance(value_dt, datetime.datetime):
            raise InvalidValueException("Value is not datetime instance '%s'" % value_dt)
        return value_dt

    @staticmethod
    def date(value_date, default=None):
        if value_date is None: return default
        if not isinstance(value_date, datetime.date):
            raise InvalidValueException("Value is not date instance '%s'" % value_date)
        return value_date

    @staticmethod
    def list(value_list, default=None):
        if value_list is None:
            return default
        if not isinstance(value_list, list):
            raise InvalidValueException("Value is not a list instance '%s'" % value_list)
        return value_list

    @staticmethod
    def dict(value_dict, default=None):
        if value_dict is None:
            return default
        if not isinstance(value_dict, dict):
            raise InvalidValueException("Value is not a dict instance '%s'" % value_dict)
        return value_dict
