#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from telegram import (ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext, CallbackQueryHandler)

from bot.constant import Text, KeyboardText
from db.model import UserVote, User, UserVoice
from setting import CHANNEL_CHAT_ID, BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

NAME, NEW_NAME, VOICE, LOCATION, BIO = range(5)
END = ConversationHandler.END
cancel_keyboard = [[KeyboardText.cancel]]


def start(update, context):
    update.message.reply_text(Text.start_description, reply_markup=ReplyKeyboardRemove())
    return END


def send_voice(update, context):
    chat_id = update.effective_chat.id
    user = User.select().where(User.chat_id == chat_id).first()
    if user:
        context.user_data['user'] = user
        update.message.reply_text(f'سلام {user.name} عزیز\n'
                                  f'وویس مورد نظرت رو آپلود یا فوروارد کن.',
                                  reply_markup=ReplyKeyboardRemove())
        return VOICE
    else:
        update.message.reply_text(Text.choose_name, reply_markup=ReplyKeyboardRemove())
        return NAME


def request_change_name(update, context):
    chat_id = update.effective_chat.id
    user = User.select().where(User.chat_id == chat_id).first()
    if user:
        context.user_data['user'] = user
        update.message.reply_text(f"اسم قبلی شما {user.name} است\n"
                                  "لطفا نام جدید خود را وارد کنید:", reply_markup=ReplyKeyboardRemove())
        return NEW_NAME
    else:
        update.message.reply_text(Text.choose_name, reply_markup=ReplyKeyboardRemove())
        return NAME


def change_name(update, context):
    name = update.message.text
    user = context.user_data['user']
    user.name = name
    user.save()
    update.message.reply_text("تغییر نام شما با موفقیت انجام شد😇\n"
                              f"نام جدید شما 👈🏻 {name}", reply_markup=ReplyKeyboardRemove())
    return END


def pick_a_name(update, context):
    name = update.message.text
    chat_id = update.effective_chat.id
    user = User.create(chat_id=chat_id, name=name, username=update.effective_chat.username)
    context.user_data['user'] = user
    update.message.reply_text(f'ممنون {name} عزیز☺️\n'
                              f'به جمع رادیو توییتر خوش اومدی🎉\n'
                              f'حالا اولین وویس خودت رو آپلود کن',
                              reply_markup=ReplyKeyboardRemove())
    return VOICE


def voice(update: Update, context: CallbackContext):
    voice_message = update.message
    # commit voice in database
    UserVoice.create(file_id=voice_message.voice.file_id,
                     chat_id=voice_message.chat_id,
                     message_id=voice_message.message_id,
                     user_username=voice_message.chat.username)
    name = context.user_data['user'].name
    name.replace(" ", "_")
    caption = "#" + name
    # if voice_message.voice.duration > int(VOICE_DURATION_LIMIT):
    #     update.message.reply_text('اوه چه زیاد😯\n'
    #                               f'زمان وویس باید کمتر از {VOICE_DURATION_LIMIT} ثانیه باشه.')
    keyboard = [
        [InlineKeyboardButton(Text.like, callback_data=Text.like + Text.separator + "0" + Text.separator + "0"),
         InlineKeyboardButton(Text.dislike, callback_data=Text.dislike + Text.separator + "0" + Text.separator + "0")]]
    context.bot.send_voice(chat_id=CHANNEL_CHAT_ID, voice=voice_message.voice, caption=caption,
                           reply_markup=InlineKeyboardMarkup(keyboard))

    update.message.reply_text('وویس شما با موفقیت به کانال ارسال شد😍')
    return END


def do_vote(vote, like_count, dislike_count):
    if vote == Text.like:
        like_count = str(int(like_count) + 1)

    elif vote == Text.dislike:
        dislike_count = str(int(dislike_count) + 1)

    return create_inline_button(like_count, dislike_count)


def do_un_vote(vote, like_count, dislike_count):
    if vote == Text.like:
        like_count = str(int(like_count) - 1)

    elif vote == Text.dislike:
        dislike_count = str(int(dislike_count) - 1)

    return create_inline_button(like_count, dislike_count)


def do_change_vote(vote, like_count, dislike_count):
    if vote == Text.like:
        dislike_count = str(int(dislike_count) - 1)
        like_count = str(int(like_count) + 1)

    elif vote == Text.dislike:
        dislike_count = str(int(dislike_count) + 1)
        like_count = str(int(like_count) - 1)

    return create_inline_button(like_count, dislike_count)


def create_inline_button(like_count, dislike_count):
    like_callback_data = Text.like + Text.separator + like_count + Text.separator + dislike_count
    dislike_callback_data = Text.dislike + Text.separator + like_count + Text.separator + dislike_count

    keyboard = [[InlineKeyboardButton(Text.like + like_count, callback_data=like_callback_data),
                 InlineKeyboardButton(Text.dislike + dislike_count, callback_data=dislike_callback_data)]]
    return keyboard


def parse_callback_data(data):
    data = data.split(Text.separator)
    vote = data[0]
    like_count = data[1]
    dislike_count = data[2]
    return vote, like_count, dislike_count


def button(update: Update, context):
    query = update.callback_query
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    if isinstance(query, CallbackQuery):
        # get passed data
        data = query.data
        vote, like_count, dislike_count = parse_callback_data(data)
        # check last user vote
        user_last_vote = UserVote.select().where(
            (UserVote.chat_id == chat_id) &
            (UserVote.message_id == message_id)).first()
        if user_last_vote:
            if user_last_vote.vote == vote:
                user_last_vote.delete_instance()
                query.answer(show_alert=True, text="You took your reaction back")
                # undo a vote
                keyboard = do_un_vote(vote, like_count, dislike_count)
            else:
                user_last_vote.vote = vote
                user_last_vote.save()
                query.answer(show_alert=True, text="You " + vote + " this")
                # change vote
                keyboard = do_change_vote(vote, like_count, dislike_count)
        else:
            UserVote.create(chat_id=chat_id, message_id=message_id, vote=vote)
            query.answer(show_alert=True, text="You " + vote + " this")
            # do vote
            keyboard = do_vote(vote, like_count, dislike_count)
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))


def cancel(update, context):
    update.message.reply_text(Text.cancel, reply_markup=ReplyKeyboardRemove())
    return END


def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)

    dp = updater.dispatcher
    send_voice_handler = ConversationHandler(
        allow_reentry=True,
        entry_points=[CommandHandler('send_voice', send_voice)],

        states={
            NAME: [MessageHandler(Filters.text, pick_a_name)],
            VOICE: [MessageHandler(Filters.voice, voice)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)]
    )
    change_name_handler = ConversationHandler(
        allow_reentry=True,
        entry_points=[CommandHandler('change_name', request_change_name)],

        states={
            NEW_NAME: [MessageHandler(Filters.text, change_name)],
            NAME: [MessageHandler(Filters.text, pick_a_name)],
        },

        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)]
    )
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(send_voice_handler)
    dp.add_handler(change_name_handler)
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()
