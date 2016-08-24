import datetime
import logging
from contextlib import contextmanager
from logging import config

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from pyboot.util import DateTimeUtil

MIME_TYPE_JSON = "application/json"


class Conf(object):
    def __init__(self, app_conf_file, logger_conf_file):
        self.app_conf_file = app_conf_file
        self.logger_conf_file = logger_conf_file
        self.app_conf = None

    def init(self):
        stream = open(self.logger_conf_file, "r")
        config.dictConfig(yaml.load(stream))
        stream.close()
        logging.debug("Logging initialized")

        stream = open(self.app_conf_file, "r")
        self.app_conf = yaml.load(stream)
        stream.close()
        logging.debug("Config initialized")
        return self

    def get(self, key, default=None):
        if key not in self.app_conf: return default
        return self.app_conf[key]

    def set(self, key, value):
        self.app_conf[key] = value


class Db(object):
    __Session = None

    def __init__(self, host=None, port=3306, username=None, password=None, db_name=None, charset="utf8",
                 init_pool_size=1, max_pool_size=5, pool_recycle_delay=600, sql_logging=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db_name = db_name
        self.charset = charset
        self.init_pool_size = init_pool_size
        self.max_pool_size = max_pool_size
        self.pool_recycle_delay = pool_recycle_delay
        self.sql_logging = sql_logging

    def init(self):
        Db.__Session = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=self.get_engine())
        logging.debug("DbConfig initialized")
        return self

    def get_engine(self):
        db_baseurl = "mysql://%s:%s@%s:%s/%s?charset=%s" % (
            self.username, self.password, self.host, self.port, self.db_name, self.charset)
        logging.info("DB Baseurl: %s, Init pool size: %s, Max pool size: %s, Pool recycle delay: %s" % (
            db_baseurl, self.init_pool_size, self.max_pool_size, self.pool_recycle_delay))
        return create_engine(db_baseurl, echo=self.sql_logging, poolclass=QueuePool, pool_size=self.init_pool_size,
                             max_overflow=int(self.max_pool_size) - int(self.init_pool_size),
                             pool_recycle=int(self.pool_recycle_delay))

    def __get_session(self):
        return Db.__Session()

    @contextmanager
    def get(self):
        start_time = datetime.datetime.now()
        db = self.__get_session()
        logging.debug("Connection time: %s milliseconds" % DateTimeUtil.diff(start_time, datetime.datetime.now()))

        try:
            yield db
        except:
            db.rollback()
            raise
        finally:
            db.close()


class DBQueryHandler(object):
    @staticmethod
    def get(db, query, one=False):
        cur = db.execute(query)
        rv = cur.fetchall()
        cur.close()
        rows = []
        for row in rv:
            rows.append(dict(zip(row.keys(), row)))

        return (rows[0] if rows else None) if one else rows

    @staticmethod
    def get_all(db, query, one=False):
        cur = db.execute(query)
        rv = cur.fetchall()
        cur.close()
        rows = []
        for row in rv:
            rows.append(row[0])
        return (rows[0] if rows else None) if one else rows

    @staticmethod
    def update(db, query):
        cur = db.execute(query)
        cur.close()
