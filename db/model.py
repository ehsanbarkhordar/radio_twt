from peewee import *

from setting import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT

my_db = PostgresqlDatabase(DATABASE_NAME,
                           user=DATABASE_USER, password=DATABASE_PASSWORD,
                           host=DATABASE_HOST, port=DATABASE_PORT)


class BaseModel(Model):
    class Meta:
        database = my_db


class User(BaseModel):
    chat_id = CharField(unique=True, primary_key=True)
    name = CharField()
    username = CharField()

    class Meta:
        table_name = 'user'


class UserVote(BaseModel):
    chat_id = BigIntegerField()
    message_id = BigIntegerField()
    vote = CharField()

    class Meta:
        table_name = 'user_vote'
