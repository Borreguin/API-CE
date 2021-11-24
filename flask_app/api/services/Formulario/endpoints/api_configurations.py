import codecs
import re
from flask_restplus import Resource
from flask import request, send_file
# importando configuraciones iniciales
import flask_app.settings.LogDefaultConfig
from flask_app.dto.mongo_class.Captcha import Captcha
from flask_app.dto.mongo_class.ConfiguracionGeneral import ConfiguracionMail
from flask_app.dto.mongo_class.Form import Formulario
from flask_app.my_lib.utils import fill_information_usuario
from flask_app.settings import initial_settings as init
from flask_app.api.services.restplus_config import api
from flask_app.api.services.restplus_config import default_error_handler
from flask_app.api.services.Formulario import parsers, serializers as srl
# importando clases para leer desde MongoDB
from flask_app.dto.mongo_class.FormTemporal import *
from flask_app.my_lib.send_mail.send_mail import *
from flask_app.my_lib.captcha.captcha_util import *
# configurando logger y el servicio web
log = flask_app.settings.LogDefaultConfig.LogDefaultConfig("ws_denuncias.log").logger
ns = api.namespace('configuracion', description='Relativas a las configuraciones generales')

ser_from = srl.FormSerializers(api)
api = ser_from.add_serializers()

regex_mail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


@ns.route('/emails/comite')
class EmailsComiteAPI(Resource):
    @api.expect(ser_from.emails)
    def post(self):
        """ Configura los emails del personal miembro de comité de ética """
        try:
            request_data = dict(request.json)
            emails = request_data.get("emails", None)
            if emails is None:
                return dict(success=False, msg="Operación incorrecta"), 400
            # check email string:
            for email in emails:
                if not re.fullmatch(regex_mail, email):
                    return dict(success=False, msg=f"El mail {email} es incorrecto"), 400
            # configurando:
            configurations = ConfiguracionMail.objects(id_config="configuracionMail").first()
            if configurations is None:
                configurations = ConfiguracionMail(emails=emails)
            else:
                configurations.emails = emails
                configurations.actualizado = dt.datetime.now()
            configurations.save()
            return dict(success=True, config=configurations.to_dict(), msg="Configuración guardada"), 200
        except Exception as e:
            return default_error_handler(e)

    def get(self):
        """ Obtiene la configuración de los emails del personal miembro de comité de ética """
        try:
            # configurando:
            configurations = ConfiguracionMail.objects(id_config="configuracionMail").first()
            if configurations is None:
                configurations = ConfiguracionMail()
            return dict(success=True, config=configurations.to_dict(), msg="Configuración obtenida"), 200
        except Exception as e:
            return default_error_handler(e)
