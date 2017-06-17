# coding: utf-8
import os

import redis
import tasktiger
from tasktiger import periodic

if 'REDIS_URL' in os.environ:
    tiger = tasktiger.TaskTiger(
        redis.Redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
    )
else:
    tiger = tasktiger.TaskTiger()

