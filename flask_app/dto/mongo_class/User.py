from mongoengine import *
import datetime as dt
import hashlib


class User(Document):
    ci = StringField(required=True, unique=True)
    nombre_apellidos = StringField(required=True, unique=True)
    correo_electronico = EmailField()
    telefono = StringField()
    cargo = StringField()
    info = DictField()
    creado = DateTimeField(default=dt.datetime.now())
    meta = {"collection": "DATA|Usuarios"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.creado is None:
            self.creado = dt.datetime.now()

    def to_dict(self):
        return dict(ci= self.ci, nombre_apellidos=self.nombre_apellidos,
                    correo_electronico=self.correo_electronico,
                    cargo=self.cargo, info=self.info,
                    creado=self.creado.strftime("%Y-%m-%d %H:%M:%S"))