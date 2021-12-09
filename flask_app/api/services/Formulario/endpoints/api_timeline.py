from flask_restplus import Resource

# importando configuraciones iniciales
import flask_app.settings.LogDefaultConfig
from flask_app.api.services.Formulario import serializers as srl
from flask_app.api.services.restplus_config import api
from flask import request
# importando clases para leer desde MongoDB
# configurando logger y el servicio web
from flask_app.dto.mongo_class.Form import Formulario
from flask_app.dto.mongo_class.Timeline import Timeline

log = flask_app.settings.LogDefaultConfig.LogDefaultConfig("ws_denuncias.log").logger
ns = api.namespace('timeline', description='Relativas al timeline de un trámite')

ser_from = srl.FormSerializers(api)
api = ser_from.add_serializers()


@ns.route('/forma/<string:id_forma>')
class TimelinePOSTAPI(Resource):

    @api.expect(ser_from.timeline)
    def post(self, id_forma: str = "Id de la forma"):
        """ Añade timeline al tramite con id_forma """
        request_data = dict(request.json)
        forma = Formulario.objects(id_forma=id_forma).first()
        if forma is None:
            return dict(success=False, forma=None, msg="No se ha encontrado información asociada"), 404
        timeline = Timeline(**request_data)
        forma.timeline.append(timeline)
        forma.save()
        return dict(success=True, forma=forma.to_dict(), timeline=timeline.to_dict(), msg="Información actualizada"), 200


@ns.route('/forma/<string:id_forma>/<string:id_timeline>')
class TimelinePUTAPI(Resource):
    @api.expect(ser_from.timeline)
    def put(self, id_forma: str = "Id de la forma", id_timeline: str = "Id del timeline"):
        """ Edita timeline del tramite con id_forma """
        request_data = dict(request.json)
        forma = Formulario.objects(id_forma=id_forma).first()
        if forma is None:
            return dict(success=False, forma=None, msg="No se ha encontrado información asociada"), 404
        success, timeline = forma.edit_timeline(id_timeline, request_data)
        if success:
            forma.save()
            return dict(success=True, forma=forma.to_dict(), timeline=timeline.to_dict(), msg="Información actualizada"), 200
        return dict(success=False, forma=None, timeline=None, msg="Timeline no encontrado"), 404