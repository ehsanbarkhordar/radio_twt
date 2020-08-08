from bot.model import db, User, UserVote
from bot.radio_twt_bot import run_bot

if __name__ == '__main__':
    db.connect()
    db.create_tables([User, UserVote])
    run_bot()
