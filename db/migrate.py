from playhouse.migrate import *

from db.model import my_db

migrator = PostgresqlMigrator(my_db)

operations = [

]
