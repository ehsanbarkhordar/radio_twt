from playhouse.migrate import *

from db.model import my_db

migrator = PostgresqlMigrator(my_db)

operations = [
    migrator.alter_column_type('user_vote', 'chat_id', BigIntegerField()),
    migrator.alter_column_type('user_vote', 'message_id', BigIntegerField()),
]
