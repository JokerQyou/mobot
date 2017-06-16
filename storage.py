# coding: utf-8
import json

import redis_wrap


class RedisStorage(object):
    '''Simple storage using Redis'''

    def __init__(self, name, prefix='mobot', system='default'):
        if not name:
            raise ValueError('Invalid storage name')

        super(RedisStorage, self).__init__()
        self.__name = '{}:{}'.format(prefix, name)
        self.__data = redis_wrap.get_hash(self.__name, system)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __getitem__(self, key):
        try:
            value = super(RedisStorage, self).__getitem__(key)
        except KeyError:
            raise
        else:
            is_json = value.startswith('{') and value.endswith('}')
            if not is_json:
                is_json = value.startswith('[') and value.endswith(']')

            if is_json:
                try:
                    return json.loads(value)
                except:
                    return value
            else:
                return value

    def __setitem__(self, key, value):
        if isinstance(value, (list, dict)):
            value = json.dumps(value, sort_keys=True)
        super(RedisStorage, self).__setitem__(key, value)


def get_storage(name, system='default'):
    '''Get a storage'''
    return RedisStorage(name, system=system)
