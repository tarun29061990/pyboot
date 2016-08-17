import logging
from contextlib import contextmanager

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from pyboot.common.conf import Conf
from pyboot.util.common import DatetimeUtil


# TODO: Need to make it non-sigleton and make it generic
class Db(object):
    __Session = None
    __instance = None

    @staticmethod
    def get_instance():
        if Db.__instance is None:
            Db.__instance = Db()
        return Db.__instance

    def init(self):
        Db.__Session = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=self.get_engine())
        logging.debug("DbConfig initialized")

    def get_engine(self):
        db_conf = Conf.get("database")
        db_baseurl = "mysql://%s/%s?charset=%s&user=%s&passwd=%s" % (
            db_conf["host"], db_conf["name"], db_conf["charset"], db_conf["user"], db_conf["password"])
        logging.info("DB Baseurl: %s, Init pool size: %s, Max pool size: %s, Pool recycle delay: %s" % (
            db_baseurl, db_conf["init_pool_size"], db_conf["max_pool_size"], db_conf["pool_recycle_delay"]))
        return create_engine(db_baseurl, echo=db_conf["sql_logging"], poolclass=QueuePool,
                             pool_size=db_conf["init_pool_size"],
                             max_overflow=int(db_conf["max_pool_size"]) - int(db_conf["init_pool_size"]),
                             pool_recycle=db_conf["pool_recycle_delay"])

    def __get_session(self):
        return Db.__Session()

    @staticmethod
    def get_db():
        return Db.get_instance().__get_session()

    @staticmethod
    @contextmanager
    def get():
        start_time = datetime.datetime.now()
        db = Db.get_db()
        logging.debug("Connection time: %s milliseconds" % DatetimeUtil.diff(start_time, datetime.datetime.now()))

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
