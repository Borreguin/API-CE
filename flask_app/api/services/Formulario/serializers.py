from flask_app.settings.initial_settings import SUPPORTED_FORMAT_DATES as time_formats
from flask_restplus import fields, Model

import datetime as dt

"""
    Configure the API HTML to show for each services the schemas that are needed 
    for posting and putting
    (Explain the arguments for each service)
    Los serializadores explican los modelos (esquemas) esperados por cada servicio
"""


class FormSerializers:

    def __init__(self, app):
        self.api = app

    def add_serializers(self):
        api = self.api

        """ serializador para formulario """
        self.forma = api.model("Información básica forma",
                               {
                                     "id_forma": fields.String(required=False,
                                                             description="Id de forma opcional"),
                                     "ci": fields.String(required=True,
                                                             description="Cédula de ciudadanía"),
                                     "nombre_apellidos": fields.String(required=True,
                                                                     description="Nombre y apellidos"),
                                     "correo_electronico": fields.String(required=True,
                                                                   description="Correo eléctronico"),
                                     "cargo": fields.String(required=True,
                                                                   description="Cargo de la persona"),
                                     "tipo_tramite": fields.String(required=True,
                                                                description="['denuncias', 'consultas']"),
                                     "telefono": fields.String(required=True,
                                                                   description="Teléfono de contacto"),
                                     "detalle_tramite": fields.String(required=True,
                                                                   description="El detalle del trámite realizado"),
                                     "archivos": fields.List(fields.String(required=False,
                                                               description="Archivos")),
                                 })

        """ serializador para usuarios """
        self.usuario = api.model("Información básica del usuario",
                               {
                                   "ci": fields.String(required=True,
                                                       description="Cédula de ciudadanía"),
                                   "nombre_apellidos": fields.String(required=True,
                                                                     description="Nombre y apellidos"),
                                   "correo_electronico": fields.String(required=True,
                                                                       description="Correo eléctronico"),
                                   "cargo": fields.String(required=True,
                                                          description="Cargo de la persona"),
                                   "telefono": fields.String(required=False,
                                                             description="Teléfono de contacto"),
                               })
        """ emails de comité de ética """
        self.emails = api.model("Lista de emails",
                                 {
                                     "emails": fields.List(fields.String, required=True, description="email individual")
                                 })
        return api
