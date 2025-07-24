from peewee import *
import os

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

class Note(BaseModel):

    query = None
    id = PrimaryKeyField()
    title = CharField()
    content = TextField()
    user = ForeignKeyField(User, backref="notes")

    class Meta:
        table_name = 'notes'



db.connect()
db.create_tables([User, Note])

print("Database connected and tables created")