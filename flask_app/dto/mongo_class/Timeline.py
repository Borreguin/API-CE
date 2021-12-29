from mongoengine import *
import datetime as dt
import uuid
from flask_app.settings import initial_settings as init


class Timeline(EmbeddedDocument):
    id_timeline = StringField(required=True, default=None)
    description = StringField(required=True, default=None)
    responsible = StringField(required=True, default="System")
    state = StringField(required=True, default=init.New, choices=init.state_list)
    updated = DateTimeField(default=dt.datetime.now())
    created = DateTimeField(default=dt.datetime.now())

    def __init__(self, *args, **values):
        super().__init__( *args, **values)
        if self.id_timeline is None:
            self.id_timeline = str(uuid.uuid4())
            self.created = dt.datetime.now()
            self.updated = self.created
        if self.description is None:
            self.description = f"Este trámite ha sido ingresado al sistema el {self.created}," \
                               f" y será analizada por el comité de ética."

    def to_dict(self):
        updated = self.updated.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.updated, dt.datetime) else self.updated
        created = self.created.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.created, dt.datetime) else self.created
        return dict(id_timeline=self.id_timeline, description=self.description, responsible=self.responsible,
                    state=self.state, updated=updated, created=created)

    def update_timeline(self, timeline_dict:dict):
        to_update = ["description", "state"]
        try:
            for key, value in timeline_dict.items():
                if key in to_update:
                    setattr(self, key, value)
            self.updated = dt.datetime.now()
            return True, "Actualizado"
        except Exception as e:
            msg = f"Error al actualizar: {str(e)}"
            return False, msg