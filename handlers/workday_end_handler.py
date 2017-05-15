# coding: utf-8
from datetime import datetime
import random

import pytz

from telegram.ext import BaseFilter, MessageHandler

TZ = pytz.timezone('Asia/Shanghai')
START = 9
END = 18


class WorkdayEndFilter(BaseFilter):

    def filter(self, message):
        # First filter by weekday: we don't work on weekends
        date = message.date.replace(tzinfo=TZ)
        if date.weekday() > 4:  # Weekdays are [0, 6]
            return False

        # Then filter by time: we work in range of [9.am, 18.pm]
        if date.hour < START or date.hour > END:
            return False

        # Then filter by message text
        text = unicode(message.text)
        keywords = (
            u'下班了',
            u'想下班',
            u'想回家',
            u'饿了',
            u'想睡觉',
            u'好困',
            u'玩游戏'
        )
        time_query_keywords = (
            u'啥时',
            u'几点',
            u'什么时候',
            u'何時',
            u'还没',
        )
        bad_words = (
            u"吃屎",
            u"药丸",
            u"执笠",
            u"倒闭",
            u"关门",
            u"散伙",
        )
        for keyword in keywords:
            if keyword in text:
                return True
            if u'下班' in text:
                for k in time_query_keywords:
                    if k in text:
                        return True
            if u'工作' in text or u"公司" in text:
                for k in bad_words:
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

    now = update.message.date.replace(tzinfo=TZ)
    end_time = datetime(now.year, now.month, now.day, hour=18, tzinfo=TZ)
    duration = end_time - now

    hour = duration.seconds / 3600
    minute = (duration.seconds % 3600) / 60
    time_remaining = '{} 小时 {} 分钟'.format(hour, minute)

    text = random.choice(text_templates).format(time_remaining)
    bot.send_message(chat_id=update.message.chat_id, text=text)


workday_end_handler = MessageHandler(WorkdayEndFilter(), workday_end_time)
