from peewee import *
from database import User, db, Note

#Connect to DB
if db.is_closed():
    db.connect()

#drop tables if they exist
db.drop_tables([Note, User])

#Recreate tables
db.create_tables([User, Note])

print("√ Tables dropped and recreated with updated schema.")