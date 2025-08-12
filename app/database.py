

import os
from datetime import datetime
from pytz import timezone

from peewee import *

# Timezone for timestamps
_eastern = timezone("US/Eastern")

# Database selection: use SQLite in tests, Postgres otherwise
if os.environ.get("TESTING") == "1":
    db = SqliteDatabase(":memory:")
else:
    # Require password from environment; provide safe local defaults for others
    db = PostgresqlDatabase(
        os.environ.get("POSTGRES_DB", "minotes"),
        user=os.environ.get("POSTGRES_USER", "minotes_user"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
    )


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    # Store a password hash (PBKDF2) instead of plaintext
    password_hash = CharField()
    email = CharField(unique=True)

    class Meta:
        table_name = "users"


class Note(BaseModel):
    title = CharField()
    content = TextField()
    user = ForeignKeyField(User, backref="notes")
    created_at = DateTimeField(default=lambda: datetime.now(_eastern))
    updated_at = DateTimeField(default=lambda: datetime.now(_eastern))
    is_active = BooleanField(default=True)  # Only the current version is active
    parent = ForeignKeyField("self", null=True, backref="versions")  # previous version
    version = IntegerField(default=1)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(_eastern)
        return super().save(*args, **kwargs)

    class Meta:
        table_name = "notes"
        indexes = (
            (("user", "created_at"), False),
            (("user", "title"), False),
        )


class UserSession(BaseModel):
    user = ForeignKeyField(User, backref="sessions")
    session_id = CharField(unique=True)
    data = TextField(null=True)  # You can store JSON string or plain text

    class Meta:
        table_name = "user_sessions"


# Initialize tables on import (simple apps)
db.connect(reuse_if_open=True)
db.create_tables([User, Note, UserSession], safe=True)