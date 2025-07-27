

import os
from datetime import datetime, timezone
from time import tzname
from peewee import *


# Use PostgresqlDatabase for cloud deployment
db = PostgresqlDatabase(
    os.environ.get("POSTGRES_DB", "minotes"),
    user=os.environ.get("POSTGRES_USER", "minotes_user"),
    password=os.environ.get("POSTGRES_PASSWORD", "JTYrCsG2wJe5mLL865eFKR39K7Pizbjr"),
    host=os.environ.get("POSTGRES_HOST", "dpg-d212lnmmcj7s73ec1j30-a"),
    port=int(os.environ.get("POSTGRES_PORT", 5432))
)


class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):

    query = None
    username = CharField(unique=True)
    password = CharField()
    email = CharField()

    class Meta:
        table_name = 'users'

from peewee import *
from datetime import datetime

class Note(BaseModel):
    title = CharField()
    content = TextField()
    user = ForeignKeyField(User, backref="notes")
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))

    is_active = BooleanField(default=True)  # Only the current version is active
    parent = ForeignKeyField('self', null=True, backref='versions')  # Reference to previous version
    version = IntegerField(default=1)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    class Meta:
        table_name = 'notes'


class UserSession(BaseModel):
    user = ForeignKeyField(User, backref="sessions")
    session_id = CharField(unique=True)
    data = TextField(null=True)  # You can store JSON string or plain text

    class Meta:
        table_name = 'user_sessions'


db.connect()
db.create_tables([User, Note, UserSession], safe=True)

print("Database connected and tables created")