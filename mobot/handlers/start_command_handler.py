# coding: utf-8
from telegram.ext import CommandHandler


def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='你好，这是一个摸豹了的机器人，可以做一些非（hao）常（wu）有（yi）趣（yi）的事情'
    )


start_command_handler = CommandHandler('start', start)
