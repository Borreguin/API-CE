from mongoengine import *
import json


class DataForm(EmbeddedDocument):
    ci = StringField(required=True, default=None)
    nombre_apellidos = StringField(required=True, default=None)
    correo_electronico = StringField(required=True, default=None)
    cargo = StringField(required=True, default=None)
    tipo_tramite = StringField(required=True, default=None)
    telefono = StringField(required=True, default=None)
    detalle_tramite = StringField(required=True, default=None)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_dict(self):
        return dict(ci=self.ci,
                    nombre_apellidos=self.nombre_apellidos,
                    correo_electronico=self.correo_electronico,
                    cargo=self.cargo, tipo_tramite=self.tipo_tramite,
                    telefono=self.telefono, detalle_tramite=self.detalle_tramite)
