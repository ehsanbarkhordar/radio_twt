from playhouse.migrate import *

from db.model import my_db

migrator = PostgresqlMigrator(my_db)

operations = [
    migrator.alter_column_type('user_vote', 'chat_id', IntegerField()),
    migrator.alter_column_type('user_vote', 'message_id', IntegerField()),
]
