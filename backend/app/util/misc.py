import datetime as dt
import locale
from typing import TypeVar
from zoneinfo import ZoneInfo

T = TypeVar("T")


def flatten_list(nested_list: list[list[T]]):
    flat_list: list[T] = []
    for sublist in nested_list:
        flat_list.extend(sublist)
    return flat_list


def format_datetime(datetime: dt.datetime, show_time: bool = True):
    locale.setlocale(locale.LC_TIME, "nl_NL.UTF-8")
    datetime_local = datetime.astimezone(ZoneInfo("Europe/Amsterdam"))
    datetime_str = datetime_local.strftime("%A %-d %B %H:%M")
    return datetime_str
