from playhouse.migrate import migrate

from db.migrate import operations
from db.model import my_db, User, UserVote, UserVoice
from bot.radio_twt_bot import run_bot

if __name__ == '__main__':
    my_db.connect()
    my_db.create_tables([User, UserVote, UserVoice])
    with my_db.atomic():
        migrate(*operations)
    run_bot()
