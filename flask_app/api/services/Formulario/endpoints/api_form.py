import codecs

from flask_restplus import Resource
from flask import request, send_file
# importando configuraciones iniciales
import flask_app.settings.LogDefaultConfig
from flask_app.dto.mongo_class.Captcha import Captcha
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
ns = api.namespace('formularios', description='Relativas a la gestión de trámites del Comité de Ética de CENACE')



ser_from = srl.FormSerializers(api)
api = ser_from.add_serializers()


@ns.route('/forma/<string:id_forma>')
class FormularioAPI(Resource):

    def get(self, id_forma: str = "Id de la forma a buscar"):
        """ Busca si una forma usando el id """
        try:
            # forma = SRNode.objects(nombre=nombre).first()
            forma = FormularioTemporal.objects(id_forma=id_forma).first()
            if forma is None:
                return dict(success=False, forma=None, msg="Información no encontrada"), 404
            return dict(success=True, forma=forma.to_dict(), msg="Información cargada"), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.forma)
    def put(self, id_forma: str = "Id de la forma a buscar"):
        """ Edita información de una forma temporal """
        try:
            request_data = dict(request.json)
            forma = FormularioTemporal.objects(id_forma=id_forma).first()
            if forma is None:
                return dict(success=False, forma=None, msg="No se ha encontrado información asociada"), 404
            forma.update_data(request_data)
            forma.save()
            return dict(success=True, forma=forma.to_dict(), msg="Información actualizada"), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/usuario/<string:ci>')
class FormularioUsuarioAPI(Resource):

    def get(self, ci: str = "Cédula del denunciante"):
        """ Busca las denuncias existentes para el usuario con CI """
        try:
            # forma = SRNode.objects(nombre=nombre).first()
            query = {'data.ci': ci}
            forma = FormularioTemporal.objects(__raw__=query).first()
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
            id_forma = request_data.get("id_forma", None)
            temp_form = FormularioTemporal.objects(id_forma=id_forma).first()
            if temp_form is not None:
                return dict(success=False, forma=None, msg="Esta forma ya existe"), 304
            forma = FormularioTemporal(data=request_data)
            forma.save()
            return dict(success=True, forma=forma.to_dict(), msg="Forma registrada de manera correcta"), 200
        except Exception as e:
            return dict(success=False, forma=None, msg=f"Error al registrar el formulario: {str(e)}"),500


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


@ns.route('/mail-temporal/<string:id_forma>')
class mailAPI(Resource):
    def post(self, id_forma):
        """ Envía mail usando informacion del formulario  """
        try:
            temp_form = FormularioTemporal.objects(id_forma=id_forma).first()
            if temp_form is None:
                return dict(success=False, msg="Los datos no han sido ingresados en el Sistema")
            # read template for notifications:
            html_template_path = os.path.join(init.TEMPLATE_REPO, "Notification.html")
            html_str = codecs.open(html_template_path, 'r', 'utf-8').read()
            # filling information:
            html_str = fill_information_usuario(html_str, temp_form)
            mail = temp_form.data["correo_electronico"]
            success, msg = send_mail(html_str, "Notificación CENACE CE", [mail], init.from_email)
            return dict(success=success, msg=msg), 200 if success else 409
        except Exception as e:
            return default_error_handler(e)