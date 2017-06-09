# coding: utf-8
from datetime import datetime
import logging
import random

import pytz

from telegram.ext import BaseFilter, Filters, MessageHandler
from telegram import ChatAction

log = logging.getLogger()
TZ = pytz.timezone('Asia/Shanghai')
START = 9
END = 18


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
        if date.weekday() > 4:  # Weekdays are [0, 6]
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
    time_remaining = ' {} 小时'.format(hour) if hour else ''
    time_remaining += ' {} 分钟'.format(minute)

    text = random.choice(text_templates).format(time_remaining)
    update.message.reply_text(text, quote=True)


workday_end_handler = MessageHandler(
    Filters.text & WorkdayEndFilter(),
    workday_end_time
)
