# coding: utf-8
import json
import logging
import multiprocessing
from multiprocessing.pool import Pool
import os

from telegram.ext import Updater
from .handlers import HANDLERS

logging.basicConfig(
    format='%(asctime)s %(name)s [%(levelname)s] %(message)s',
    level=logging.INFO
)
CONFIG = os.environ.get(
    'CONFIG_FILE',
    os.path.join(os.path.dirname(__file__), '..', 'config.json')
)


def start_taskqueue_workers():
    from .taskqueue import tiger
    p = multiprocessing.Process(target=tiger.run_worker)
    p.daemon = True
    p.start()
    return
    pool = Pool(4)
    pool.map_async(tiger.run_worker, [None, None]).wait()


def main():
    with open(CONFIG) as crf:
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

    start_taskqueue_workers()

    updater.start_polling(poll_interval=2, bootstrap_retries=5)
    updater.idle()


if __name__ == '__main__':
    main()
