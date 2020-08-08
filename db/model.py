import datetime

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
    created_at = DateTimeField(default=datetime.datetime.now)
    is_premium = BooleanField(default=False)

    class Meta:
        table_name = 'user'


class UserVote(BaseModel):
    chat_id = BigIntegerField()
    message_id = BigIntegerField()
    vote = CharField()

    class Meta:
        table_name = 'user_vote'


class UserVoice(BaseModel):
    file_id = CharField(unique=True, primary_key=True)
    chat_id = BigIntegerField()
    message_id = BigIntegerField()
    user_username = CharField()

