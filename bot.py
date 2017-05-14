# coding: utf-8
import json
import logging


from telegram.ext import Updater
from handlers import HANDLERS

logging.basicConfig(
    format='%(asctime)s %(name)s [%(levelname)s] %(message)s',
    level=logging.INFO
)


def main():
    with open('config.json') as crf:
        config = json.load(crf)
        token = config['token']
        proxy = config.get('proxy', None)

    if proxy:
        updater = Updater(token, request_kwargs={'proxy_url': proxy})
    else:
        updater = Updater(token)

    dispatcher = updater.dispatcher
    for handler in HANDLERS:
        dispatcher.add_handler(handler)

    updater.start_polling(poll_interval=2, bootstrap_retries=5)
    updater.idle()


if __name__ == '__main__':
    main()
