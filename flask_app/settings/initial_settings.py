# Created by Roberto Sanchez at 3/29/2019
# -*- coding: utf-8 -*-
""" Set the initial settings of this application"""
import os
from .config import config as raw_config

""""
    If you need more information. Please contact the email above: rg.sanchez.a@gmail.com
    "My work is well done to honor God at any time" R Sanchez A.
    Mateo 6:33
"""

""" script path"""
settings_path = os.path.dirname(os.path.abspath(__file__))
api_path = os.path.dirname(settings_path)
project_path = os.path.dirname(api_path)

""" initial configuration """
config = raw_config

""" Defining whether is the production environment or not """
production_path = os.path.join(project_path, "Production_server.txt")
print(production_path, os.path.exists(production_path))
if os.path.exists(production_path):
    PRODUCTION_ENV = True
    config["DEBUG"] = False
    DEBUG = False
else:
    PRODUCTION_ENV = False

TESTING_ENV = os.getenv('testing_env', None) == 'True'

if PRODUCTION_ENV:
    """ Production environment """
    from flask_app.settings.env.prod import prod
    config.update(prod)
    DEBUG = False
else:
    """ Developer environment """
    from flask_app.settings.env.dev import dev
    config.update(dev)
    DEBUG = config["DEBUG"]


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

""" SUPPORTED DATES """
SUPPORTED_FORMAT_DATES = config["SUPPORTED_FORMAT_DATES"]
DEFAULT_DATE_FORMAT = config["DEFAULT_DATE_FORMAT"]

""" SWAGGER CONFIGURATION """
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = config["RESTPLUS_SWAGGER_UI_DOC_EXPANSION"]
RESTPLUS_VALIDATE = config["RESTPLUS_VALIDATE"]
RESTPLUS_MASK_SWAGGER = config["RESTPLUS_MASK_SWAGGER"]
RESTPLUS_ERROR_404_HELP = config["RESTPLUS_ERROR_404_HELP"]
API_PREFIX = config["API_PREFIX"]
API_PORT = config["API_PORT"] if PRODUCTION_ENV else config["DEBUG_PORT"]
DEBUG_PORT = config["DEBUG_PORT"]
VERSION = config["version"]
SECRET_KEY = config["SECRET_KEY"]
HOSTNAME = config["HOSTNAME"]
HOSTNAME_URL = config["HOSTNAME_URL"]

""" Mail configurations """
from_email = config["from_email"]

SQLALCHEMY_DATABASE_URI = config["SQLALCHEMY_DATABASE_URI"]
SQLALCHEMY_TRACK_MODIFICATIONS = config["SQLALCHEMY_TRACK_MODIFICATIONS"]

"""" FILE REPO CONFIGURATION """
FILE_REPO = config["FILE_REPO"]
LOGS_REPO = config["LOGS_REPO"]
REPOS = [FILE_REPO, LOGS_REPO]
FINAL_REPOS = list()
for repo in REPOS:
    repo = os.path.join(project_path, repo)
    FINAL_REPOS.append(repo)
    if not os.path.exists(repo):
        os.makedirs(repo)

[FILE_REPO, LOGS_REPO] = FINAL_REPOS

TEMPLATE_REPO = os.path.join(api_path, "templates")

""" Application """

New, in_progress, stopped, finished = "Inicio de proceso", "En trámite", "Detenido", "Finalizado"
state_list = [New, in_progress, stopped, finished]