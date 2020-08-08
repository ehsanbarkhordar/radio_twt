#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from telegram import (ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext, CallbackQueryHandler)

# Enable logging
from bot.constant import like, dislike
from db.model import UserVote
from setting import CHANNEL_CHAT_ID, BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

NAME, VOICE, LOCATION, BIO = range(4)


def start(update, context):
    update.message.reply_text(
        'سلام😀\n'
        'اول اسمتو وارد کن👇\n'
        'ــــ لزوما نمیخواد اسم واقعیت باشه و میتونه لقب یا اسم اکانت توییترت باشه😉 ــــ',
        reply_markup=ReplyKeyboardRemove())
    return NAME


def pick_a_name(update, context):
    name = update.message.text
    # logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(f'ممنون {name} عزیز☺️\n'
                              f'به جمع رادیو توییتر خوش اومدی🎉\n'
                              f'حالا اولین وویس خودت رو آپلود کن',
                              reply_markup=ReplyKeyboardRemove())

    return VOICE


def voice(update: Update, context: CallbackContext):
    voice_message = update.message
    name = "احسان"
    caption = "#" + name
    keyboard = [[InlineKeyboardButton(like, callback_data=like + "-0-0"),
                 InlineKeyboardButton(dislike, callback_data=dislike + "-0-0")]]
    context.bot.send_voice(chat_id=CHANNEL_CHAT_ID, voice=voice_message.voice, caption=caption,
                           reply_markup=InlineKeyboardMarkup(keyboard))

    update.message.reply_text('وویس شما با موفقیت به کانال ارسال شد😍')
    return ConversationHandler.END


def do_vote(vote, like_count, dislike_count):
    if vote == like:
        like_count = str(int(like_count) + 1)

    elif vote == dislike:
        dislike_count = str(int(dislike_count) + 1)

    like_callback_data = like + "-" + like_count + "-" + dislike_count
    dislike_callback_data = dislike + "-" + like_count + "-" + dislike_count

    keyboard = [[InlineKeyboardButton(like + like_count, callback_data=like_callback_data),
                 InlineKeyboardButton(dislike + dislike_count, callback_data=dislike_callback_data)]]
    return keyboard


def do_un_vote(vote, like_count, dislike_count):
    if vote == like:
        like_count = str(int(like_count) - 1)

    elif vote == dislike:
        dislike_count = str(int(dislike_count) - 1)

    like_callback_data = like + "-" + like_count + "-" + dislike_count
    dislike_callback_data = dislike + "-" + like_count + "-" + dislike_count

    keyboard = [[InlineKeyboardButton(like + like_count, callback_data=like_callback_data),
                 InlineKeyboardButton(dislike + dislike_count, callback_data=dislike_callback_data)]]
    return keyboard


def do_change_vote(vote, like_count, dislike_count):
    if vote == like:
        dislike_count = str(int(dislike_count) + 1)
        like_count = str(int(like_count) - 1)

    elif vote == dislike:
        dislike_count = str(int(dislike_count) - 1)
        like_count = str(int(like_count) + 1)

    like_callback_data = like + "-" + like_count + "-" + dislike_count
    dislike_callback_data = dislike + "-" + like_count + "-" + dislike_count

    keyboard = [[InlineKeyboardButton(like + like_count, callback_data=like_callback_data),
                 InlineKeyboardButton(dislike + dislike_count, callback_data=dislike_callback_data)]]
    return keyboard


def parse_callback_data(data):
    vote = data.split("-")[0]
    like_count = data.split("-")[1]
    dislike_count = data.split("-")[2]
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
            (UserVote.message_id == message_id))
        if user_last_vote:
            if user_last_vote == vote:
                user_last_vote.delete_instance()
                query.answer(show_alert=True, text="You took your reaction back")
                # undo a vote
                keyboard = do_un_vote(vote, like_count, dislike_count)
            else:
                user_last_vote.update(vote=vote)
                query.answer(show_alert=True, text="You " + vote + " this")
                # change vote
                keyboard = do_change_vote()
        else:
            UserVote.create(chat_id=chat_id, message_id=message_id, vote=vote)
            query.answer(show_alert=True, text="You " + vote + " this")
            # do vote
            keyboard = do_vote(vote, like_count, dislike_count)
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))


def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Maybe I can visit you sometime! '
                              'At last, tell me something about yourself.')

    return BIO


def skip_location(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'At last, tell me something about yourself.')

    return BIO


def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def run_bot():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            NAME: [MessageHandler(Filters.text, pick_a_name)],

            VOICE: [MessageHandler(Filters.voice, voice)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
