from flask_restplus import Resource
from flask import request, send_file
import re, os
# importando configuraciones iniciales
from settings import initial_settings as init
from api.services.restplus_config import api
from api.services.restplus_config import default_error_handler
from api.services.Formulario import serializers as srl
from api.services.Formulario import parsers
# importando clases para leer desde MongoDB
from my_lib.mongo_engine_handler.Form import *
from my_lib.send_mail.send_mail import *
from my_lib.captcha.captcha_util import *
# configurando logger y el servicio web
log = init.LogDefaultConfig("ws_denuncias.log").logger
ns = api.namespace('formularios', description='Relativas a la gestión de trámites del Comité de Ética de CENACE')



ser_from = srl.FormSerializers(api)
api = ser_from.add_serializers()


@ns.route('/forma/<string:id_forma>')
class FormularioAPI(Resource):

    def get(self, id_forma: str = "Id de la forma a buscar"):
        """ Busca si una forma usando el id """
        try:
            # forma = SRNode.objects(nombre=nombre).first()
            forma = Formulario.objects(id_forma=id_forma).first()
            if forma is None:
                return dict(success=False), 404
            return forma.to_dict(), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/usuario/<string:ci>')
class FormularioUsuarioAPI(Resource):

    def get(self, ci: str = "Cédula del denunciante"):
        """ Busca las denuncias existentes para el usuario con CI """
        try:
            # forma = SRNode.objects(nombre=nombre).first()
            query = {'data.ci': ci}
            forma = Formulario.objects(__raw__=query).first()
            if forma is None:
                return dict(success=False), 404
            return forma.to_dict(), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/forma')
class FormularioPostAPI(Resource):
    @api.expect(ser_from.forma)
    def post(self):
        """ Postea una forma en el servidor """
        try:
            request_data = dict(request.json)
            forma = Formulario(data=request_data)
            forma.save()
            return forma.to_dict(), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/forma/<string:id_forma>/evidencias')
class EvidenciasAPI(Resource):
    @api.response(200, 'Archivo subido correctamente')
    @api.expect(parsers.file_upload)
    def post(self, id_forma):
        try:
            args = parsers.file_upload.parse_args()
            filename = args['file'].filename
            stream_file = args['file'].stream.read()
            # verificar existencia de folder
            destination = os.path.join(init.FILE_REPO, id_forma)
            if not os.path.exists(destination):
                os.makedirs(destination)
            # path del archivo a guardar
            destination = os.path.join(destination, filename)
            with open(destination, 'wb') as f:
                f.write(stream_file)
            return dict(success=True), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/captcha/<string:id>')
class CaptchaAPI(Resource):
    def post(self, id):
        text, image = gen_captcha(6)
        captcha = Captcha(id_captcha=id,text=text)
        captcha.save()
        return send_file(image, as_attachment=False,
                         attachment_filename=f'{id}.png',
                         mimetype='image/png')


@ns.route('/captcha/<string:id>/<string:value>/verified')
class VerifiedCaptchaAPI(Resource):
    def get(self, id, value):
        try:
            captcha = Captcha.objects(id_captcha=id).first()
            if captcha is None:
                return dict(success=False, errors="No se encontró el captcha en referencia"), 400
            if captcha.text == value:
                return dict(success=True), 200
            else:
                return dict(success=False), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/evidencia')
class EvidenciaAPI(Resource):
    @api.response(200, 'Archivo subido correctamente')
    @api.expect(parsers.file_upload)
    def post(self):
        try:
            args = parsers.file_upload.parse_args()
            filename = args['file'].filename
            stream_file = args['file'].stream.read()
            # verificar existencia de folder
            destination = os.path.join(init.FILE_REPO, "temp")
            if not os.path.exists(destination):
                os.makedirs(destination)
            # path del archivo a guardar
            destination = os.path.join(destination, filename)
            with open(destination, 'wb') as f:
                f.write(stream_file)
            return dict(success=True), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/mail')
class mailAPI(Resource):
    @api.expect(ser_from.forma)
    def post(self):
        """ Envía mail usando informacion del formulario  """
        try:
            request_data = dict(request.json)
            mail = request_data["correo_electronico"]

            str_html = "<div> <h1>Notificación</h1> <div> Esta es una simple notifiación. " \
                       "Posteriormente se puede añadir más elementos a esta notificación </div>" \
                       "<br></br>" \
                       f"{request_data}" \
                       "</div>"
            send_mail(str_html, "Notificación CENACE CE", [mail, "mbautista@cenace.org.ec"], "cenace_ce@cenace.org.ec")
            return 200
        except Exception as e:
            return default_error_handler(e)