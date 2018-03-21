# coding: utf-8
import logging
import multiprocessing
# from multiprocessing.pool import Pool

from telegram.ext import Updater
from .handlers import HANDLERS
from . import CONFIG

logging.basicConfig(
    format='%(asctime)s %(name)s [%(levelname)s] %(message)s',
    level=logging.INFO
)


def start_taskqueue_workers():
    '''
    Start task queue worker(s), currently using a single process.
    '''
    from .handlers import PERIODIC_TASKS
    from .taskqueue import tiger, clear_queue
    # 删除之前的所有任务
    clear_queue()
    # 添加任务
    for func, period_ in PERIODIC_TASKS:
        tiger.task(schedule=period_, unique=True)(func)()
        logging.info('Task %s scheduled at %s', func, period_)

    # 创建并运行 worker
    p = multiprocessing.Process(target=tiger.run_worker)
    p.daemon = True
    p.start()
    return


def main():
    token = CONFIG['token']
    proxy = CONFIG.get('proxy', None)

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
