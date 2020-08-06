#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from telegram import (ReplyKeyboardRemove, Update)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext)

# Enable logging
from bot.setting import CHANNEL_CHAT_ID, BOT_TOKEN

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
    context.bot.send_voice(chat_id=CHANNEL_CHAT_ID, voice=voice_message.voice)
    update.message.reply_text('وویس شما با موفقیت به کانال ارسال شد😍')
    return LOCATION


def not_voice(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return LOCATION


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

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],

            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
