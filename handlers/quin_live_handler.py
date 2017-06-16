# coding: utf-8
'''
Notice:
Credits to https://github.com/Yven/zaima for live stream detection and random memes.

秦喵喵谁不爱呢
'''
import logging
import random
import time

import pytz
import requests
import tasktiger

# from telegram.ext import BaseFilter, Filters, MessageHandler
from telegram.ext import CommandHandler
from telegram import Bot
from storage import get_storage

log = logging.getLogger()
TZ = pytz.timezone('Asia/Shanghai')
tiger = tasktiger.TaskTiger()


def random_quin_meme():
    '''
    Return random meme by Mr.Quin
    '''
    return random.choice((
        '摸了。',
        '秦先森已经歇了。',
        '什么？已经八点了？',
        '靠妖啊，秦先森又在吃香香鸡了。',
        '秦喵喵再不播我就要死了。',
        'zaima',
        '不在，cnm',
        '戳木娘啊，秦川又去哪里摸鱼了。',
        '你能表演一下那个吗？',
        '每天都在那里直播。',
        '狗才摸鱼。',
        '别问了，秦川这种生物不存在的。',
        'zaima？男娼堇业代表。',
        '怕不是要摸爆一切。',
        '怕不是要摸到时间的尽头。',
        '秦川什么时候来舞动青春啊。',
        '说不出话。',
    ))


def random_quin_nick():
    '''
    Return random nickname of Mr.Quin
    '''
    return random.choice((
        '秦川', '秦先森', '秦喵喵', '秦智障', '川川子', '机核摸鱼王奎恩',
        'Quin', '缺', '缺哥哥', '缺神', 'Q酱', '二五仔',
    ))


def is_quin_live(live):
    '''
    Return proper text according to given JSON API response
    '''
    if not live['error']:
        live = live['data']
        quin_live_url = 'http://douyu.com/quin'
        if live['room_status'] == '1':
            return (
                '惊了！{}居然播了，不敢信。'
                '而且有{}个猛男在看直播，整个房间都gay gay的。 {}'
            ).format(random_quin_nick(), live['online'], quin_live_url)


@tiger.task(schedule=tasktiger.periodic(minutes=10), unique=True)
def check_quin_live(token):
    with get_storage('quin_livestream') as store:
        # 开播后每 1 小时检查一次
        if time.time() - store.get('streaming', 0) < 60 * 60:
            return

    api_url = 'http://open.douyucdn.cn/api/RoomApi/room/3614'
    try:
        data = requests.get(
            api_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',  # noqa
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,ja-JP;q=0.8,ja;q=0.6,zh-CN;q=0.4,zh;q=0.2,en;q=0.2',
                'DNT': '1',
                'Host': 'open.douyucdn.cn',
                'Upgrade-Insecure-Requests': '1',
            },
            timeout=5
        ).json()
    except Exception as e:
        print e
    else:
        text = is_quin_live(data)
        if text:
            bot = Bot(token)
            with get_storage('quin_livestream') as store:
                store['streaming'] = time.time()
                for chat in store['subscriptions']:
                    bot.send_message(chat, text)


def sub_quin_live(bot, update):
    new_subscription = False
    with get_storage('quin_livestream') as store:
        if update.message.chat_id not in store['subscriptions']:
            store['subscriptions'] = store['subscriptions'] + [update.message.chat_id]
            new_subscription = True

    if new_subscription:
        update.message.reply_text(
            '订阅成功。每 10 分钟检查一次，如果 {} 开播会告诉你的。'.format(
                random_quin_nick()
            )
        )
        check_quin_live(bot.token)


def unsub_quin_live(bot, update):
    with get_storage('quin_livestream') as store:
        if update.message.chat_id in store['subscriptions']:
            subs = store['subscriptions']
            subs.remove(update.message.chat_id)
            store['subscriptions'] = subs
            update.message.reply_text('哦')
        else:
            update.message.reply_text('都还没订阅，智障啊')


quin_live_sub_handler = CommandHandler('sublive', sub_quin_live)
quin_live_unsub_handler = CommandHandler('unsublive', unsub_quin_live)
