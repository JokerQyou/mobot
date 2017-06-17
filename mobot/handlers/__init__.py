# coding: utf-8
from .workday_end_handler import workday_end_handler
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
)
PERIODIC_TASKS = [
    (check_quin_livestream_periodic, periodic(minutes=10)),
]
__all__ = ['HANDLERS', 'PERIODIC_TASKS', ]
