# coding: utf-8
import json
import os

CONFIG_FILE = os.environ.get(
    'CONFIG_FILE',
    os.path.join(os.path.dirname(__file__), '..', 'config.json')
)
with open(CONFIG_FILE) as crf:
    CONFIG = json.load(crf)
