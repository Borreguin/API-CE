from mongoengine import *
import datetime as dt
import hashlib

from flask_app.dto.mongo_class.DataForm import DataForm


class FormularioTemporal(Document):
    id_forma = StringField(required=True, unique=True, default=None)
    data = EmbeddedDocumentField(DataForm, required=True)
    created = DateTimeField(default=dt.datetime.now())
    actualizado = DateTimeField(default=dt.datetime.now())
    meta = {"collection": "Temporal|Form", 'indexes': [{
        'fields': ['created'],
        'expireAfterSeconds': 2592000
    }]}

    # Dar 1 mes de existencia = 3600*24*30

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        id = str(dt.datetime.now()) + str(self.data["ci"])
        if self.id_forma is None:
            self.id_forma = hashlib.md5(id.encode()).hexdigest()[:8]
            self.actualizado = dt.datetime.now()

    def to_dict(self):
        return dict(id_forma=self.id_forma, data=self.data.to_dict(),
                    actualizado=self.actualizado.strftime("%Y-%m-%d %H:%M:%S"))

    def to_object(self):
        return dict(id_forma=self.id_forma, data=self.data, created=self.created,
                    actualizado=self.actualizado)

    def update_data(self, data_dict: dict):
        data_dict.pop("id_forma", None)
        self.data = DataForm(**data_dict)
        self.actualizado = dt.datetime.now()
