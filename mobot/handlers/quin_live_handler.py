# coding: utf-8
'''
Notice:

Credits to https://github.com/Yven/zaima
 for live stream detection and random memes.

秦喵喵谁不爱呢
'''
import logging
import random
import time

import pytz
import requests

# from telegram.ext import BaseFilter, Filters, MessageHandler
from telegram.ext import CommandHandler
from telegram import Bot
from ..storage import get_set, get_hash
from .. import CONFIG

log = logging.getLogger()
TZ = pytz.timezone('Asia/Shanghai')
SUB_LIST = 'quin_livestream:subscription'
STORE_HASH = 'quin_livestream:store'
LIVESTREAM_URL = 'http://douyu.com/quin'


def random_quin_nick():
    '''
    Return random nickname of Mr.Quin
    '''
    return random.choice((
        '秦川', '秦先森', '秦喵喵', '秦智障', '川川子', '机核摸鱼王奎恩',
        'Quin', '缺', '缺哥哥', '缺神', 'Q酱', '二五仔',
    ))


def is_quin_streaming():
    '''
    Check if Mr.Quin is currently streaming
    Returns (<bool> is_streaming, <int> number_of_audience)
    '''
    api_url = 'http://open.douyucdn.cn/api/RoomApi/room/3614'
    try:
        print('checking quin livestram')
        data = requests.get(
            api_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',  # noqa
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',  # noqa
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,ja-JP;q=0.8,ja;q=0.6,zh-CN;q=0.4,zh;q=0.2,en;q=0.2',  # noqa
                'DNT': '1',
                'Host': 'open.douyucdn.cn',
                'Upgrade-Insecure-Requests': '1',
            },
            timeout=5
        ).json()
    except:
        audience_count = 0
        is_streaming = False
    else:
        if not data['error']:
            live = data['data']
            is_streaming = live['room_status'] == '1'
            audience_count = live.get('online', 0)
        else:
            audience_count = 0
            is_streaming = False
    finally:
        return is_streaming, audience_count


def check_quin_livestream_for_new_sub(update):
    '''Check livestream status for new subscriber'''
    is_streaming, audience_count = is_quin_streaming()
    if is_streaming:
        update.message.reply_text(
            (
                '惊了！{}居然播了，不敢信。'
                '而且有{}个猛男在看直播，整个房间都gay gay的。 {}'
            ).format(random_quin_nick(), audience_count, LIVESTREAM_URL),
            quote=True
        )
    else:
        update.message.reply_text(
            '很遗憾，{}现在正在摸鱼'.format(random_quin_nick()), quote=True
        )


def check_quin_livestream_periodic():
    '''
    定时触发的直播检查，检查逻辑：
    - 如果上一次检查发现开播了：
      - 如果上一次检查是在少于 1 小时前进行的：
        - 不进行操作（1 小时内认为是连播，并且不需要检查状态）
      - 否则：
        - 进行检查，并且记录直播状态和检查时间，但不需要通知
    - 如果上次检查发现没有开播，检查直播状态
      - 如果开播了：记录直播状态和检查时间，并发送通知
      - 如果没有开播：记录直播状态和检查时间
    '''
    store = get_hash(STORE_HASH)

    if store.get('is_streaming', 'false') == 'true':
        if time.time() - float(store.get('last_check', 0)) < 60 * 60:
            return
        else:
            is_streaming, _ = is_quin_streaming()
            store.update({
                'last_check': time.time(),
                'is_streaming': ('true' if is_streaming else 'false'),
            })
    else:
        is_streaming, audience_count = is_quin_streaming()
        store.update({
            'last_check': time.time(),
            'is_streaming': ('true' if is_streaming else 'false'),
        })
        if is_streaming:
            bot = Bot(CONFIG['token'])
            for subscriber in get_set(SUB_LIST):
                try:
                    bot.send_message(
                        (
                            '惊了！{}居然播了，不敢信。'
                            '而且有{}个猛男在看直播，整个房间都gay gay的。 {}'
                        ).format(
                            random_quin_nick(), audience_count, LIVESTREAM_URL
                        )
                    )
                except:
                    pass

        else:
            pass


def sub_quin_live(bot, update):
    '''
    新订阅者处理器
    - 将订阅者会话 ID 追加到推送列表
    - 为此订阅者单独查询一次直播状态
      (TODO:根据上次检查时间和状态来决定是否单独检查)
    '''
    subs = get_set(SUB_LIST)
    if update.message.chat_id in subs:
        update.message.reply_text('活尸化严重啊，订阅过了都不记得的吗')
    else:
        subs.add(update.message.chat_id)
        update.message.reply_text(
            '订阅好了。每 10 分钟检查一次，如果{}开播会告诉你的。'.format(
                random_quin_nick()
            ),
            quote=True
        )
        check_quin_livestream_for_new_sub(update)


def unsub_quin_live(bot, update):
    '''
    解除订阅处理器
    - 将订阅者会话 ID 从推送列表移除
    - 发送一个不明所以的回复
    '''
    subs = get_set(SUB_LIST)
    if update.message.chat_id in subs:
        subs.remove(update.message.chat_id)
        update.message.reply_text('哦')
    else:
        update.message.reply_text('都还没订阅，智障啊')


quin_live_sub_handler = CommandHandler('sublive', sub_quin_live)
quin_live_unsub_handler = CommandHandler('unsublive', unsub_quin_live)
