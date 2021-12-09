import uuid
from mongoengine import *
import datetime as dt

from flask_app.dto.mongo_class.DataForm import DataForm
from flask_app.dto.mongo_class.Timeline import Timeline


class Formulario(Document):
    id_forma = StringField(required=True, unique=True, default=None)
    data = EmbeddedDocumentField(DataForm, required=True)
    timeline = ListField(EmbeddedDocumentField(Timeline), required=True, default=[Timeline()])
    created = DateTimeField(default=dt.datetime.now())
    actualizado = DateTimeField(default=dt.datetime.now())
    meta = {"collection": "DATA|Formulario"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.id_forma is None:
            self.id_forma = str(uuid.uuid4())
            self.actualizado = dt.datetime.now()

    def to_dict(self):
        return dict(id_forma=self.id_forma, data=self.data.to_dict(), timeline=[t.to_dict() for t in self.timeline],
                    actualizado=self.actualizado.strftime("%Y-%m-%d %H:%M:%S"))

    def edit_timeline(self, id_timeline, timeline_dict: dict):
        for idx, tl in enumerate(self.timeline):
            if id_timeline == tl.id_timeline:
                self.timeline[idx].update_timeline(timeline_dict)
                return True, self.timeline[idx]
        return False, None
