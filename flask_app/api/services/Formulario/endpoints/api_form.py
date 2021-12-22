import codecs

from flask_restplus import Resource
from flask import request, send_file, send_from_directory
# importando configuraciones iniciales
import flask_app.settings.LogDefaultConfig
from flask_app.dto.mongo_class.Captcha import Captcha
from flask_app.dto.mongo_class.ConfiguracionGeneral import ConfiguracionMail
from flask_app.dto.mongo_class.Form import Formulario
from flask_app.my_lib.utils import fill_information_usuario, get_files_for, set_max_age_to_response, \
    fill_timeline_notification
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
        """ Busca si una forma definitiva aceptada vía correo electrónico """
        forma = Formulario.objects(id_forma=id_forma).first()
        if forma is None:
            return dict(success=False, forma=None, msg="Información no encontrada"), 404
        files = get_files_for(id_forma)
        return dict(success=True, forma=forma.to_dict(), files=files, msg="Información cargada"), 200

    @api.expect(ser_from.forma)
    def put(self, id_forma: str = "Id de la forma a buscar"):
        """ Edita información de una forma temporal """
        request_data = dict(request.json)
        forma = FormularioTemporal.objects(id_forma=id_forma).first()
        if forma is None:
            return dict(success=False, forma=None, msg="No se ha encontrado información asociada"), 404
        forma.update_data(request_data)
        forma.save()
        return dict(success=True, forma=forma.to_dict(), msg="Información actualizada"), 200


@ns.route('/forma-temporal/<string:id_forma>')
class FormularioTemporalAPI(Resource):

    def get(self, id_forma: str = "Id de la forma a buscar"):
        """ Busca si una forma temporal insertada mediante formulario """
        forma = FormularioTemporal.objects(id_forma=id_forma).first()
        if forma is None:
            return dict(success=False, forma=None, msg="Información no encontrada"), 404
        files = get_files_for(id_forma)
        return dict(success=True, forma=forma.to_dict(), files=files, msg="Información cargada"), 200


@ns.route('/usuario/<string:ci>')
class FormularioUsuarioAPI(Resource):

    def get(self, ci: str = "Cédula del denunciante"):
        """ Busca las denuncias existentes para el usuario con CI """
        # forma = SRNode.objects(nombre=nombre).first()
        query = {'data.ci': ci}
        forma = FormularioTemporal.objects(__raw__=query).first()
        if forma is None:
            return dict(success=False), 404
        return forma.to_dict(), 200


@ns.route('/forma')
class FormularioPostAPI(Resource):
    @api.expect(ser_from.forma)
    def post(self):
        """ Postea una forma en el servidor """
        request_data = dict(request.json)
        id_forma = request_data.get("id_forma", None)
        temp_form = FormularioTemporal.objects(id_forma=id_forma).first()
        if temp_form is not None:
            return dict(success=False, forma=None, msg="Esta forma ya existe"), 304
        request_data.pop("id_forma", None)
        forma = FormularioTemporal(data=DataForm(**request_data))
        forma.save()
        return dict(success=True, forma=forma.to_dict(), msg="Forma registrada de manera correcta"), 200


@ns.route('/forma-temporal/<string:id_forma>/evidencias')
class EvidenciasAPI(Resource):
    @api.response(200, 'Archivo subido correctamente')
    @api.expect(parsers.file_upload)
    def post(self, id_forma):
        """ Subir archivos de evidencia a la forma (id_forma)"""
        args = parsers.file_upload.parse_args()
        filename = args['file'].filename
        stream_file = args['file'].stream.read()
        # verificar existencia de folder
        destination = os.path.join(init.FILE_REPO, id_forma)
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
            except:
                log.info(f"This file already exists {destination}")
        # path del archivo a guardar
        file_path = os.path.join(destination, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'wb') as f:
            f.write(stream_file)
        return dict(success=True, msg=f" {filename} - This file was upload"), 200


@ns.route('/forma/<string:id_forma>/evidencias/<string:file>')
class EvidenciasFileAPI(Resource):

    def get(self, id_forma, file):
        """ Obtiene un archivo subido al expediente """
        form_path = os.path.join(init.FILE_REPO, id_forma)
        file_path = os.path.join(form_path, file)
        if not os.path.exists(file_path):
            return dict(success=False, msg="Archivo no encontrado"), 404
        response = send_from_directory(os.path.dirname(file_path), file, as_attachment=True)
        return set_max_age_to_response(response, 30)

    def delete(self, id_forma, file):
        """ Elimina un archivo subido al expediente """
        form_path = os.path.join(init.FILE_REPO, id_forma)
        file_path = os.path.join(form_path, file)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return dict(success=False, msg="Archivo no encontrado"), 404
        os.remove(file_path)
        files = get_files_for(id_forma)
        return dict(success=True, files=files, msg="Archivo eliminado"), 200


@ns.route('/captcha/<string:id>')
class CaptchaAPI(Resource):
    def post(self, id):
        """ Crea un nuevo Captcha """
        text, image = gen_captcha(6)
        captcha = Captcha(id_captcha=id,text=text)
        captcha.save()
        return send_file(image, as_attachment=False,
                         attachment_filename=f'{id}.png',
                         mimetype='image/png')


@ns.route('/captcha/<string:id>/<string:value>/verified')
class VerifiedCaptchaAPI(Resource):
    def get(self, id, value):
        """ Verifica si el código ingresado corresponde al código captcha generado """
        captcha = Captcha.objects(id_captcha=id).first()
        if captcha is None:
            return dict(success=False, errors="No se encontró el captcha en referencia"), 400
        if captcha.text == value:
            return dict(success=True), 200
        else:
            return dict(success=False), 200


@ns.route('/evidencia')
class EvidenciaAPI(Resource):
    @api.response(200, 'Archivo subido correctamente')
    @api.expect(parsers.file_upload)
    def post(self):
        """ Añade archivos de evidencia en la carpeta temporal """
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


@ns.route('/mail-temporal/<string:id_forma>')
class mailAPI(Resource):
    def post(self, id_forma):
        """ Envía mail usando informacion del formulario  """
        temp_form = FormularioTemporal.objects(id_forma=id_forma).first()
        if temp_form is None:
            return dict(success=False, msg="Los datos no han sido ingresados en el Sistema")
        # read template for notifications:
        html_template_path = os.path.join(init.TEMPLATE_REPO, "Notification.html")
        html_str = codecs.open(html_template_path, 'r', 'utf-8').read()
        # filling information:
        html_str = fill_information_usuario(html_str, temp_form, get_files_for(id_forma))
        mail = temp_form.data["correo_electronico"]
        success, msg = send_mail(html_str, "Notificación CENACE CE", [mail], init.from_email)
        return dict(success=success, msg=msg), 200 if success else 409


@ns.route('')
class FormsAPI(Resource):
    def get(self):
        """ Obtiene todos los trámites ingresados a la plataforma """
        result = list()
        for form in Formulario.objects:
            result.append(form.to_dict())
        return dict(success=True, forms=result, msg="Lista de trámites"), 200
