# coding: utf-8
from datetime import datetime
import pytz
from tzlocal import get_localzone

from .workday_end_handler import (
    workday_end_handler, notify_offwork_daily,
    offwork_sub_handler, offwork_unsub_handler,
    TZ,
)
from .start_command_handler import start_command_handler
from .quin_live_handler import (
    quin_live_sub_handler, quin_live_unsub_handler,
    check_quin_livestream_periodic,
)
from ..taskqueue import periodic

HANDLERS = (
    workday_end_handler,
    start_command_handler,
    quin_live_sub_handler,
    quin_live_unsub_handler,
    offwork_sub_handler,
    offwork_unsub_handler,
)

offwork_start = get_localzone().normalize(
    TZ.localize(datetime(2000, 1, 1, hour=18))
).replace(tzinfo=None)
PERIODIC_TASKS = [
    (check_quin_livestream_periodic, periodic(minutes=5)),
    (notify_offwork_daily, periodic(days=1, start_date=offwork_start)),
]
__all__ = ['HANDLERS', 'PERIODIC_TASKS', ]
