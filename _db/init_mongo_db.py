# Init script for MongoDB community server (if needed)

import os, sys
from sys import platform
import subprocess as sb         # sub
import traceback  # Seguimiento de errores

script_path = os.path.dirname(os.path.abspath(__file__))  # absolute script path
project_path = os.path.dirname(script_path)
# db_path = os.path.join(script_path, "mongo_db")
db_path = None
sys.path.append(project_path)


log_path = os.path.join(script_path, "../logs")
config = dict()
config["MONGO_LOG_LEVEL"] = {"value": "OFF", "options": ["ON", "OFF"]}
MONGO_LOG_LEVEL = "OFF"
MONGO_PORT = 2717


def linux_config():
    return None


def mac_config():
    return ["mongod", "--config", "/opt/homebrew/etc/mongod.conf"]


def windows_config():
    path_v4_2 = 'C:\\Program Files\\MongoDB\\Server\\4.2\\bin\\mongod.exe'
    path_v4_4 = 'C:\\Program Files\\MongoDB\\Server\\4.4\\bin\\mongod.exe'

    if os.path.exists(path_v4_2):
        mongo_exe = path_v4_2
    elif os.path.exists(path_v4_4):
        mongo_exe = path_v4_4
    else:
        print("No se encontro el path para levantar mongodb")
        mongo_exe = None

    if db_path is None:
        to_run = f"{mongo_exe} --dbpath {db_path} --port {MONGO_PORT}"
    else:
        to_run = f"{mongo_exe} --port {MONGO_PORT}"
    return to_run


def to_execute():
    if platform == "linux" or platform == "linux2":
        # linux
        pass
    elif platform == "darwin":
        # OS X
        to_run = mac_config()
    elif platform == "win32":
        # Windows...
        # command to run:
        mongo_exe = windows_config()

    return to_run


def start_mongodb_service():
    # check if db path and log path exists otherwise create them
    if db_path is not None and not os.path.exists(db_path):
        os.makedirs(db_path)
    if db_path is not None and not os.path.exists(log_path):
        os.makedirs(log_path)
    # used in case there is no mongo service
    to_run = to_execute()

    print(f"Executing: {to_run}")
    # if is needed to save logs about database
    otp = None
    if MONGO_LOG_LEVEL in config["MONGO_LOG_LEVEL"]["options"]:
        if MONGO_LOG_LEVEL == "ON":
            otp = open(os.path.join(log_path, "mongoDb.log"), "w")
        else:
            otp = None
    sb.Popen(to_run, stdout=otp)
    return True


if __name__ == "__main__":
    try:
        if start_mongodb_service():
            print("El servicio de mongodb ha empezado correctamente")
            if MONGO_LOG_LEVEL == "ON":
                print("WARNING!! El log de la base de datos MongoDB está activado. "
                      "Esto puede llenar de manera rápida el espacio en disco")
    except Exception as e:
        print(f"Problemas al empezar el servicio: \n {str(e)} \n {traceback.format_exc()}")


