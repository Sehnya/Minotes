from peewee import *


db = SqliteDatabase('notes.db')

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

    class Meta:
        table_name = 'notes'



db.connect()
db.create_tables([User, Note])

print("Database connected and tables created")