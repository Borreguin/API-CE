import os
config = dict()

config["name"] = "settings"
config["version"] = "1.5"

config["FLASK_SERVER_NAME"] = "localhost:7077"
config["FLASK_DEBUG"] = False

# Configuración de la librería API:
config["RESTPLUS_SWAGGER_UI_DOC_EXPANSION"] = "list"
config["RESTPLUS_VALIDATE"] = True
config["RESTPLUS_MASK_SWAGGER"] = False
config["RESTPLUS_ERROR_404_HELP"] = True
config["API_PREFIX"] = '/api'
config["API_PORT"] = 7820
config["DEBUG_PORT"] = 5000

config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

config["ROTATING_FILE_HANDLER_HELP"] = "https://docs.python.org/3.6/library/logging.handlers.html#logging.handlers.RotatingFileHandler.__init__",
config["ROTATING_FILE_HANDLER"] = {"filename": "app_flask.log", "maxBytes": 5000000, "backupCount": 5, "mode": "a"}
config["ROTATING_FILE_HANDLER_LOG_LEVEL"] = {"value": "info", "options": ["error", "warning", "info", "debug", "off"]}

# MONGODB CONFIGURATION
config["MONGOCLIENT_SETTINGS"] = {"host": "localhost", "port": 27017, "db": "DB_CE_CENACE"}
config["MONGO_LOG_LEVEL"] = {"value": "OFF", "options": ["ON", "OFF"]}

# FILE repository:
config["DB_REPO"] = "_db"
config["FILE_REPO"] = os.path.join(config["DB_REPO"], "files")

config["SUPPORTED_FORMAT_DATES"] = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S.%f"]
config["DEFAULT_DATE_FORMAT"] = "%Y-%m-%d %H:%M:%S"
