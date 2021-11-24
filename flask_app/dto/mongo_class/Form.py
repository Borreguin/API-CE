from mongoengine import *
import datetime as dt
import hashlib


class Formulario(Document):
    id_forma = StringField(required=True, unique=True, default=None)
    data = DictField(required=True)
    created = DateTimeField(default=dt.datetime.now())
    actualizado = DateTimeField(default=dt.datetime.now())
    meta = {"collection": "DATA|Formulario"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.id_forma is None:
            id = str(dt.datetime.now()) + str(self.data["ci"])
            self.id_forma = hashlib.md5(id.encode()).hexdigest()[:7]
            self.actualizado = dt.datetime.now()

    def to_dict(self):
        return dict(id_forma=self.id_forma, data=self.data,
                    actualizado=str(self.actualizado))
