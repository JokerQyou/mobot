# coding: utf-8
from .workday_end_handler import workday_end_handler
from .start_command_handler import start_command_handler
from .quin_live_handler import quin_live_handler

HANDLERS = (
    workday_end_handler,
    start_command_handler,
    quin_live_handler,
)
__all__ = HANDLERS
