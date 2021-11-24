from mongoengine import *
import datetime as dt


class ConfiguracionMail(Document):
    id_config = StringField(default="configuracionMail")
    emails = ListField(StringField())
    actualizado = DateTimeField(default=dt.datetime.now())
    meta = {"collection": "CNFG|General"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

    def to_dict(self):
        return dict(id_config=self.id_config,
            emails=self.emails, actualizado=str(self.actualizado))