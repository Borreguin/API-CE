import datetime as dt

from mongoengine import Document, StringField, DateTimeField


class Captcha(Document):
    id_captcha = StringField(required=True, unique=True)
    text = StringField(required=True, unique=True)
    created = DateTimeField(default=dt.datetime.now())
    meta = {"collection": "CNFG|Captcha", 'indexes': [{
                'fields': ['created'],
                'expireAfterSeconds': 36000
            }]}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.created = dt.datetime.now()