# coding: utf-8
'''
Notice:
All credits to https://github.com/Yven/zaima for live stream detection and random memes.

秦喵喵谁不爱呢
'''
from datetime import datetime
import logging
import random

import pytz
import requests

# from telegram.ext import BaseFilter, Filters, MessageHandler
from telegram.ext import CommandHandler

log = logging.getLogger()
TZ = pytz.timezone('Asia/Shanghai')


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
    if live['error']:
        text = '好神秘啊，怕不是进错房间了？'
    else:
        live = live['data']
        quin_live_url = 'http://douyu.com/quin'
        if live['room_status'] == '1':
            text = (
                '惊了！{}居然播了，不敢信。'
                '而且有{}个猛男在看直播，整个房间都gay gay的。 {}'
            ).format(random_quin_nick(), live['online'], quin_live_url)
        elif live['room_status'] == '2':
            now = TZ.normalize(datetime.utcnow().replace(tzinfo=pytz.utc))
            last_live = TZ.localize(datetime.strptime(live['start_time'], '%Y-%m-%d %H:%M'))
            rest_duration = now - last_live
            # Rested for less than one day
            if rest_duration.days == 0:
                text = '刚刚勃完，让{}歇一歇吧，不要猝死在直播间。'.format(random_quin_nick())
            else:
                text = '{}已经摸了 {} 天 {} 小时 {} 分钟了。\n{}'.format(
                    random_quin_nick(),
                    rest_duration.days,
                    rest_duration.seconds // 3600,
                    rest_duration.seconds % 3600 // 60,
                    random_quin_meme()
                )
        else:
            text = '斗鱼怎么了，简直说不出话。'

    return text


def check_quin_live(bot, update):
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
    except requests.RequestException as e:
        return bot.send_message(chat_id=update.message.chat_id, text='出事儿啦！{}'.format(e.message))
    else:
        text = is_quin_live(data)
        bot.send_message(chat_id=update.message.chat_id, text=text)


quin_live_handler = CommandHandler('live', check_quin_live)
