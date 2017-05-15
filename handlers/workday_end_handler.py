# coding: utf-8
from datetime import datetime
import logging
import random

import pytz

from telegram.ext import BaseFilter, Filters, MessageHandler

log = logging.getLogger()
TZ = pytz.timezone('Asia/Shanghai')
START = 9
END = 18


class WorkdayEndFilter(BaseFilter):

    def filter(self, message):
        # First filter by weekday: we don't work on weekends
        date = TZ.normalize(message.date.replace(tzinfo=pytz.utc))
        if date.weekday() > 4:  # Weekdays are [0, 6]
            return False

        # Then filter by time: we work in range of [9.am, 18.pm]
        if date.hour < START or date.hour > END:
            return False

        # Then filter by message text
        text = message.text
        keywords = (u'下班了', u'想下班', u'想回家', )
        time_query_keywords = (u'啥时', u'几点', u'什么时候', u'何時', )
        for keyword in keywords:
            if keyword in text:
                return True
            if u'下班' in text:
                for k in time_query_keywords:
                    if k in text:
                        return True

        return False


def workday_end_time(bot, update):
    text_templates = (
        '{}之后就能去做些快乐的事情了',
        '离下班还有{}',
        '还有{}就下班了',
        '敬业时间还剩{}',
        '再敬业{}就能歇了',
    )

    now = TZ.normalize(update.message.date.replace(tzinfo=pytz.utc))
    end_time = TZ.localize(datetime(now.year, now.month, now.day, hour=18))
    duration = end_time - now

    hour = duration.seconds // 3600
    minute = (duration.seconds % 3600) // 60
    time_remaining = ' {} 小时 {} 分钟'.format(hour, minute)

    text = random.choice(text_templates).format(time_remaining)
    bot.send_message(chat_id=update.message.chat_id, text=text)


workday_end_handler = MessageHandler(Filters.text & WorkdayEndFilter(), workday_end_time)
