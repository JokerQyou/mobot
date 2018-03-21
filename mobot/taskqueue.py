# coding: utf-8
import logging
import os

import redis
import tasktiger
from tasktiger import periodic, Task

if 'REDIS_URL' in os.environ:
    tiger = tasktiger.TaskTiger(
        redis.Redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
    )
else:
    tiger = tasktiger.TaskTiger()


def clear_queue():
    '''
    Clears all inactive tasks from queue.
    '''
    for queue, stats in tiger.get_queue_stats().items():
        for state, tasks in stats.items():
            if state == 'error':
                for task in Task.tasks_from_queue(tiger, queue, state)[-1]:
                    task.delete()
                    logging.info('Task %s cleared from queue %s', task, queue)
            elif state == 'scheduled':
                for task in Task.tasks_from_queue(tiger, queue, state)[-1]:
                    task.cancel()
                    logging.info('Task %s cleared from queue %s', task, queue)
