import codecs

from flask_restplus import Resource
from flask import request, send_file
# importando configuraciones iniciales
import flask_app.settings.LogDefaultConfig
from flask_app.dto.mongo_class.Captcha import Captcha
from flask_app.dto.mongo_class.ConfiguracionGeneral import ConfiguracionMail
from flask_app.dto.mongo_class.Form import Formulario
from flask_app.my_lib.utils import fill_information_usuario, fill_information_comite
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
ns = api.namespace('confirmacion', description='Relativas a la confirmación del requerimiento')

ser_from = srl.FormSerializers(api)
api = ser_from.add_serializers()


@ns.route('/<string:id_forma>')
class ConfirmacionAPI(Resource):

    def post(self, id_forma: str = "Id de la forma a buscar"):
        """ Acepta un trámite usando el id """
        try:
            # forma = SRNode.objects(nombre=nombre).first()
            forma = FormularioTemporal.objects(id_forma=id_forma).first()
            formaFinalDB = Formulario.objects(id_forma=id_forma).first()
            # existe la forma temporal?
            if forma is None:
                return dict(success=False, forma=None, msg="Información no encontrada"), 404
            # existe la forma final?
            if formaFinalDB is not None:
                return dict(success=False, forma=None, msg="Esta información ya ha sido registrada en el sistema"), 409
            # si no existe entonces guarde en base de datos:
            formaFinal = Formulario(**forma.to_dict())
            formaFinal.save()
            return dict(success=True, forma=formaFinal.to_dict(), msg="Información cargada"), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/mail/<string:id_forma>')
class ConfirmacionMailAPI(Resource):

    def post(self, id_forma: str = "Id de la forma a buscar"):
        """ Envía mail de confirmación """
        try:
            # forma = SRNode.objects(nombre=nombre).first()
            formaFinalDB = Formulario.objects(id_forma=id_forma).first()
            # existe la forma final?
            if formaFinalDB is None:
                return dict(success=False, forma=None, msg="No existe información asociada"), 404
            # enviar información
            html_template_path = os.path.join(init.TEMPLATE_REPO, "Notification_Comite.html")
            html_str = codecs.open(html_template_path, 'r', 'utf-8').read()
            # filling information:
            html_str = fill_information_comite(html_str, formaFinalDB)
            # mail configuration:
            config = ConfiguracionMail.objects(id_config="configuracionMail").first()
            if config is None:
                return dict(success=True, msg="La información de mail aún no ha sido configurada")
            # send information to Comite:
            success, msg = send_mail(html_str, "Notificación CENACE para el Comité de Ética",
                                     config.emails, init.from_email)
            msg = "Se ha enviado de manera correcta la notificación al comité de Ética de CENACE. " \
                  "Luego del análisis recibirá más información del estado de su trámite" if success else msg
            return dict(success=success, msg=msg), 200 if success else 409
        except Exception as e:
            return default_error_handler(e)