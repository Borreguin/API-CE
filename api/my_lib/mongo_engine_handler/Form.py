from mongoengine import *
import datetime as dt
import hashlib


class Formulario(Document):
    id_forma = StringField(required=True, unique=True)
    data=DictField(required=True)
    actualizado = DateTimeField(default=dt.datetime.now())
    meta = {"collection": "DATA|Formulario"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        id = str(dt.datetime.now()) + str(self.data["ci"])
        self.id_forma = hashlib.md5(id.encode()).hexdigest()[:6]
        self.actualizado = dt.datetime.now()

    def to_dict(self):
        return dict(id_forma=self.id_forma, data=self.data,
                    actualizado=self.actualizado.strftime("%Y-%m-%d %H:%M:%S"))


class Captcha(Document):
    id_captcha = StringField(required=True, unique=True)
    text = StringField(required=True, unique=True)
    created = DateTimeField(default=dt.datetime.now())
    meta = {"collection": "CNF|Captcha", 'indexes': [{
                'fields': ['created'],
                'expireAfterSeconds': 36000
            }]}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.created = dt.datetime.now()