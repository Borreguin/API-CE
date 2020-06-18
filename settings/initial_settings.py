# Created by Roberto Sanchez at 3/29/2019
# -*- coding: utf-8 -*-
""" Set the initial settings of this application"""
import sys
import pymongo as pm
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
import logging
import subprocess
import os
from .config import config as raw_config

""""
    Created by Roberto Sánchez A, based on the Master Thesis:
    "A proposed method for unsupervised anomaly detection for a multivariate building dataset "
    University of Bern/Neutchatel/Fribourg - 2017
    Any copy of this code should be notified at rg.sanchez.a@gmail.com; you can redistribute it
    and/or modify it under the terms of the MIT License.

    If you need more information. Please contact the email above: rg.sanchez.a@gmail.com
    "My work is well done to honor God at any time" R Sanchez A.
    Mateo 6:33
"""

""" script path"""
script_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(script_path)

""" initial configuration """
config = raw_config

"""" FLASK CONFIGURATION """
FLASK_SERVER_NAME = config["FLASK_SERVER_NAME"]
FLASK_DEBUG = config["FLASK_DEBUG"]

""" Log file settings: """
sR_node_name = config["ROTATING_FILE_HANDLER"]["filename"]
log_path = os.path.join(project_path, "logs")
log_file_name = os.path.join(log_path, sR_node_name)
config["ROTATING_FILE_HANDLER"]["filename"] = log_file_name
ROTATING_FILE_HANDLER = config["ROTATING_FILE_HANDLER"]
ROTATING_FILE_HANDLER_LOG_LEVEL = config["ROTATING_FILE_HANDLER_LOG_LEVEL"]

""" Settings for Mongo Client"""
MONGOCLIENT_SETTINGS = config["MONGOCLIENT_SETTINGS"]
MONGO_LOG_LEVEL = config["MONGO_LOG_LEVEL"]["value"]
MONGO_LOG_LEVEL_OPTIONS = config["MONGO_LOG_LEVEL"]["options"]

if FLASK_DEBUG:
    MONGOCLIENT_SETTINGS.update(dict(db="DB_TEST"))

""" Configuration of Mongo Engine """
"""
Connections in MongoEngine are registered globally and are identified with aliases
Therefore no need to initialize other connections. 
"""

""" SUPPORTED DATES """
SUPPORTED_FORMAT_DATES = config["SUPPORTED_FORMAT_DATES"]
DEFAULT_DATE_FORMAT = config["DEFAULT_DATE_FORMAT"]



RESTPLUS_SWAGGER_UI_DOC_EXPANSION = config["RESTPLUS_SWAGGER_UI_DOC_EXPANSION"]
RESTPLUS_VALIDATE = config["RESTPLUS_VALIDATE"]
RESTPLUS_MASK_SWAGGER = config["RESTPLUS_MASK_SWAGGER"]
RESTPLUS_ERROR_404_HELP = config["RESTPLUS_ERROR_404_HELP"]

SQLALCHEMY_DATABASE_URI = config["SQLALCHEMY_DATABASE_URI"]
SQLALCHEMY_TRACK_MODIFICATIONS = config["SQLALCHEMY_TRACK_MODIFICATIONS"]

"""" FILE REPO CONFIGURATION """
FILE_REPO = config["FILE_REPO"]
FILE_REPO = os.path.join(project_path, FILE_REPO)
if not os.path.exists(FILE_REPO):
    os.makedirs(FILE_REPO)


class LogDefaultConfig():
    """
    Default configuration for the logger file:
    """
    rotating_file_handler = None

    def __init__(self, log_name: str = None):
        if log_name is None:
            log_name = "Default.log"

        self.log_file_name = os.path.join(log_path, log_name)
        self.rotating_file_handler = ROTATING_FILE_HANDLER
        self.rotating_file_handler["filename"] = self.log_file_name
        logger = logging.getLogger(log_name)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        # creating rotating and stream Handler
        R_handler = RotatingFileHandler(**self.rotating_file_handler)
        R_handler.setFormatter(formatter)
        S_handler = StreamHandler(sys.stdout)
        # adding handlers:
        logger.addHandler(R_handler)
        logger.addHandler(S_handler)

        # setting logger in class
        self.logger = logger

        self.level = ROTATING_FILE_HANDLER_LOG_LEVEL["value"]
        options = ROTATING_FILE_HANDLER_LOG_LEVEL["options"]
        if self.level in options:
            if self.level == "error":
                self.logger.setLevel(logging.ERROR)
            if self.level == "warning":
                self.logger.setLevel(logging.WARNING)
            if self.level == "debug":
                self.logger.setLevel(logging.DEBUG)
            if self.level == "info":
                self.logger.setLevel(logging.INFO)
            if self.level == "off":
                self.logger.setLevel(logging.NOTSET)
        else:
            self.logger.setLevel(logging.ERROR)


def main():
    pass


if __name__ == '__main__':
    main()
