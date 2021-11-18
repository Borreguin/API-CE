from flask_restplus import Resource
from flask import request, send_file
import re, os
# importando configuraciones iniciales
from api.settings import initial_settings as init
from api.services.restplus_config import api
from api.services.restplus_config import default_error_handler
from api.services.Formulario import serializers as srl
from api.services.Formulario import parsers
# importando clases para leer desde MongoDB
from api.my_lib.mongo_engine_handler.User import *
from api.my_lib.send_mail.send_mail import *
from api.my_lib.captcha.captcha_util import *
# configurando logger y el servicio web
log = init.LogDefaultConfig("ws_users.log").logger
ns = api.namespace('users', description='Relativas a los usuarios del Comité de Ética de CENACE')

ser_from = srl.FormSerializers(api)
api = ser_from.add_serializers()


@ns.route('/user/<string:ci>')
class UserAPI(Resource):
    def get(self, ci: str = "Cédula del usuario"):
        """ Busca un usuario mediante su número de cédula """
        try:
            # forma = SRNode.objects(nombre=nombre).first()
            user = User.objects(ci=ci).first()
            if user is None:
                return dict(success=False, msg="Usuario no encontrado"), 404
            return dict(success=True, user=user.to_dict()), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.usuario)
    def post(self, ci: str = "Cédula del usuario"):
        """ Ingresa un usuario mediante su número de cédula
            Si el usuario ya existe entonces error 409
        """
        try:
            # forma = SRNode.objects(nombre=nombre).first()
            user = User.objects(ci=ci).first()
            request_data = dict(request.json)
            if user is not None:
                return dict(success=False, msg="Usuario ya existe"), 409
            user = User(**request_data)
            user.save()
            return dict(success=True, user=user.to_dict()), 200
        except Exception as e:
            return default_error_handler(e)