# coding: utf-8
from datetime import datetime
import logging
import random

import pytz

from telegram.ext import BaseFilter, Filters, MessageHandler, CommandHandler
from telegram import ChatAction, Bot
from ..cn_holidays import is_workday
from ..storage import get_hash, get_set
from .. import CONFIG

log = logging.getLogger(__name__)
TZ = pytz.timezone('Asia/Shanghai')
START = 9
END = 18
STORE_HASH = 'offwork_notify:store'
SUB_LIST = 'offwork_notify:subscription'


class WorkdayEndFilter(BaseFilter):

    def _bad_keyword_detect(self, text):
        keywords = (
            '公司',
            '项目',
            '工作'
        )
        bad_words = (
            '药丸',
            '倒闭',
            '执笠',  # 倒闭
            '散伙',
            '收档',  # 关门
        )
        for i in keywords:
            if i in text:
                for j in bad_words:
                    if j in text:
                        return True
        return False

    def _keyword_detect(self, text):
        keywords = (
            '下班了',
            '想下班',
            '想回家',
            '想返屋企',
            '好眼瞓',  # 很困
            '想睡觉',
            '要补休',
            '想摸鱼',
            '不想醒目',
        )
        time_query_keywords = (
            '啥时',
            '几点',
            '什么时候',
            '何時',
            '几时',
            '多久',
        )
        eye_catching_keywords = (
            '多久',
            '还要',
            '你们最好',
        )
        for keyword in keywords:
            if keyword in text:
                return True
            if u'下班' in text:
                for k in time_query_keywords:
                    if k in text:
                        return True
            if u'醒目' in text:
                for k in eye_catching_keywords:
                    if k in text:
                        return True
        return False

    def filter(self, message):
        # First filter by weekday: we don't work on weekends
        date = TZ.normalize(message.date.replace(tzinfo=pytz.utc))
        if not is_workday(date):
            return False

        # Then filter by time: we work in range of [9.am, 18.pm]
        if date.hour < START or date.hour >= END:
            return False

        # Then filter by message text
        text = message.text

        if self._bad_keyword_detect(text) or self._keyword_detect(text):
            return True

        return False


def workday_end_time(bot, update):
    bot.sendChatAction(
        chat_id=update.message.chat_id, action=ChatAction.TYPING
    )
    text_templates = (
        '{}之后就能去做些快乐的事情了',
        '离下班还有{}',
        '还有{}就下班了',
        '敬业时间还剩{}',
        '再敬业{}就能歇了',
        '还要醒目{}',
        '剩余醒目时间: {}',
    )

    now = TZ.normalize(update.message.date.replace(tzinfo=pytz.utc))
    end_time = TZ.localize(datetime(now.year, now.month, now.day, hour=18))
    duration = end_time - now

    hour = duration.seconds // 3600
    minute = (duration.seconds % 3600) // 60
    second = duration.seconds % 60
    time_remaining = ' {} 小时'.format(hour) if hour else ''
    time_remaining += ' {} 分钟'.format(minute) if minute else ''
    time_remaining += ' {} 秒'.format(second) if second else ''

    text = random.choice(text_templates).format(time_remaining)
    update.message.reply_text(text, quote=True)


workday_end_handler = MessageHandler(
    Filters.text & WorkdayEndFilter(),
    workday_end_time
)


def sub_offwork_notify(bot, update):
    subs = get_set(SUB_LIST)
    if update.message.chat_id in subs:
        update.message.reply_text(
            '活尸化严重啊，订阅过了都不记得的吗', quote=True
        )
    else:
        subs.add(update.message.chat_id)
        update.message.reply_text('好的，下次摸鱼带上你', quote=True)


def unsub_offwork_notify(bot, update):
    subs = get_set(SUB_LIST)
    if update.message.chat_id in subs:
        subs.remove(update.message.chat_id)
        update.message.reply_text('哦', quote=True)
    else:
        update.message.reply_text('都还没订阅，智障啊', quote=True)


offwork_sub_handler = CommandHandler('submo', sub_offwork_notify)
offwork_unsub_handler = CommandHandler('unsubmo', unsub_offwork_notify)


def random_offwork_meme():
    return random.choice((
        '该摸了', '我摸了，你们随意', '溜了溜了', '下班',
    ))


def notify_offwork_daily():
    '''
    Send a notification to all subscribers if current time is around end_time
    '''
    now = TZ.normalize(datetime.utcnow().replace(tzinfo=pytz.utc))
    end_time = TZ.localize(datetime(now.year, now.month, now.day, hour=18))
    if not is_workday(now):
        return

    offset = end_time - now
    if -60 < offset.total_seconds() <= 0:
        log.info('Offwork time reached, sending push notifications')
        bot = Bot(CONFIG['token'])
        for subscriber in get_set(SUB_LIST):
            try:
                bot.send_message(subscriber, random_offwork_meme())
            except:
                log.exception(
                    'Failed to send offwork notification to %s', subscriber
                )
