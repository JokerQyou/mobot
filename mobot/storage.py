# coding: utf-8
import json
import os

import redis_wrap

PREFIX = 'mobot'
REDIS_NAME = 'default'
REDIS_DB = 1

if 'REDIS_URL' in os.environ:
    import redis
    redis_wrap.SYSTEMS[REDIS_NAME] = redis.Redis.from_url(
        os.environ['REDIS_URL'], db=REDIS_DB, decode_responses=True
    )


def get_set(name, system=REDIS_NAME):
    return redis_wrap.get_set('{}:{}'.format(PREFIX, name), system=system)


def get_list(name, system=REDIS_NAME):
    return redis_wrap.get_list('{}:{}'.format(PREFIX, name), system=system)


def get_hash(name, system=REDIS_NAME):
    return redis_wrap.get_hash('{}:{}'.format(PREFIX, name), system=system)


def get_bitset(name, system=REDIS_NAME):
    return redis_wrap.get_bitset('{}:{}'.format(PREFIX, name), system=system)
