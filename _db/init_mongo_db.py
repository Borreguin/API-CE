# Script de inicialización de Base de Datos MongoDB

import os, sys
import subprocess as sb  # Procesos en paralelo
import traceback  # Seguimiento de errores

script_path = os.path.dirname(os.path.abspath(__file__))  # obtener el path absoluto de este script
project_path = os.path.dirname(script_path)
sys.path.append(project_path)

db_path = os.path.join(script_path, "", "../mongo_db")
path_v4_2 = 'C:\\Program Files\\MongoDB\\Server\\4.2\\bin\\mongod.exe'
path_v4_4 = 'C:\\Program Files\\MongoDB\\Server\\4.4\\bin\\mongod.exe'

if os.path.exists(path_v4_2):
    mongo_exe = path_v4_2
elif os.path.exists(path_v4_4):
    mongo_exe = path_v4_4
else:
    print("No se encontro el path para levantar mongodb")

log_path = os.path.join(script_path, "../logs")
config = dict()
config["MONGO_LOG_LEVEL"] = {"value": "OFF", "options": ["ON", "OFF"]}
MONGO_LOG_LEVEL = "OFF"
MONGO_PORT = 2717


def start_mongodb_service():
    # check if db path and log path exists otherwise create them
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # command to run:
    to_run = f"{mongo_exe} --dbpath {db_path} --port {MONGO_PORT}"
    print(f"Se ejecutará: {to_run}")
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
