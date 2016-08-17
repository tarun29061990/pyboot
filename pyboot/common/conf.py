import logging
from logging import config

import yaml

MIME_TYPE_JSON = "application/json"
API_MAX_RECORDS = 25


# TODO: Need to make it non-sigleton and make it generic
class Conf(object):
    __instance = None

    def __init__(self):
        self.app_conf = None

    @staticmethod
    def get_instance():
        if Conf.__instance is None:
            Conf.__instance = Conf()
        return Conf.__instance

    def init(self, app_conf_path, logger_conf_path):
        stream = open(logger_conf_path, "r")
        config.dictConfig(yaml.load(stream))
        stream.close()
        logging.debug("Logging initialized")

        stream = open(app_conf_path, "r")
        self.app_conf = yaml.load(stream)
        stream.close()
        logging.debug("Config initialized")

    def get_value(self, key, default=None):
        if key not in self.app_conf: return default
        return self.app_conf[key]

    def set_value(self, key, value):
        self.app_conf[key] = value

    @staticmethod
    def get(key, default=None):
        return Conf.get_instance().get_value(key, default)

    @staticmethod
    def set(key, value):
        Conf.get_instance().set_value(key, value)
