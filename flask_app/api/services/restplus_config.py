"""
    This file defines all the API's configuration - API Home Page
    Archivo que define la configuración de la API en General - página inicial de la API
    Adds:
        Logger to save all the problems in the API
        Error handler in case is needed
"""

import traceback
from flask import request
import datetime as dt
from flask_restplus import Api
from sqlalchemy.orm.exc import NoResultFound
from flask_app.settings.LogDefaultConfig import LogDefaultConfig
from flask_app.settings.initial_settings import MONGOCLIENT_SETTINGS

""" mongo client config"""
from pymongo import MongoClient
mongo_client = MONGOCLIENT_SETTINGS
dup_key_error = "duplicate key error"
import re

api_log = LogDefaultConfig("api_services.log").logger

api = Api(version='0.1', title='API - Sistema de registro de denuncias del Comité Ética - CENACE',
          contact="Roberto Sánchez A",
          contact_email="rg.sanchez.a@gmail.com",
          contact_url="https://github.com/Borreguin",
          description='Esta API permite gestionar denuncias para el Comité de Ética de CENACE',
          ordered=True)


@api.errorhandler(Exception)
def default_error_handler(e):
    global api_log
    ts = dt.datetime.now().strftime('[%Y-%b-%d %H:%M:%S.%f]')
    msg = f"{ts} {request.remote_addr} {request.method} {request.scheme}" \
          f"{request.full_path}"
    api_log.error(msg)
    api_log.error(traceback.format_exc())
    if hasattr(e, 'data'):
        return dict(success=False, errors=str(e.data["errors"])), 400
    if dup_key_error in str(e):

        r_exp = "collection: (.*) index:"
        db, collection = re.search(r_exp, str(e)).group(1).split(".")
        db_c = mongo_client.pop('db', None)
        if db != db_c:
            print(f"No hay coincidencia de base de datos: se esperaba {db} pero se encuentra configurado: {db_c}")
        r_exp = "key: {(.*)}"
        key, value = re.search(r_exp, str(e)).group(1).strip().split(":")
        filter_dict = {key.strip(): value.replace('"', "").strip()}
        client = MongoClient(**mongo_client)
        collection_to_search = client[db][collection]
        conflict_object = collection_to_search.find_one(filter_dict)
        client.close()
        to_send, n = dict(), 0
        for k in conflict_object.keys():
            if n > 4:
                to_send["mas_detalles_en"] = str(conflict_object["_id"])
                break
            elif "id" not in k:
                to_send[k] = str(conflict_object[k])
            n += 1
        return dict(success=False, errors=f"Error de llave duplicada: "
                                          f"Existen conflicto con elemento ya existente: {filter_dict}",
                    details=to_send)
    return dict(success=False, errors=str(e)), 500

    # if not FLASK_DEBUG:
    #    return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    api_log.warning(traceback.format_exc())
    return {'message': 'No se obtuvo resultado'}, 404
