from peewee import *

from bot.setting import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT

db = PostgresqlDatabase(DATABASE_NAME,
                        user=DATABASE_USER, password=DATABASE_PASSWORD,
                        host=DATABASE_HOST, port=DATABASE_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    chat_id = CharField(unique=True, primary_key=True)
    name = CharField()
    username = CharField()


class UserVote(BaseModel):
    chat_id = CharField()
    message_id = CharField()
    vote = CharField()
