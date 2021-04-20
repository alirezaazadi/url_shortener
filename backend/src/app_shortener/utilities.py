import datetime
import hashlib
import random
from datetime import datetime as dt
from datetime import timedelta

import base62
from django.utils import timezone
from django.utils.timezone import make_aware


def generate_random_string(original_string: str, base_string: str = None, result_length: int = 8) -> str:
    """
    Generate a fixed size random string based on the passed string.
    :param string base_string: if passed, it will be part of the generated random string.
    :param string original_string: the original string.
    :param int result_length: length of returned string.
    :return:
    """
    if base_string:
        return base_string

    return base62.encodebytes(hashlib.md5(original_string.encode()).digest())[:result_length]


def get_n_unit_ago(base=None, **kwargs):
    return (timezone.now() - timedelta(**kwargs)) if not base else (base - timedelta(**kwargs))


def get_date_range(date):
    """
    Convert a date to a range which begin from the begging
    time of the date and ends with the end of it.
    :param date:
    :return:
    """
    return [make_aware(datetime.datetime.combine(date, datetime.time.min)),
            make_aware(datetime.datetime.combine(date, datetime.time.max))]


def random_date(start, end):
    """
    return a random datetime between two datetime objects.
    """
    return dt.fromtimestamp(random.uniform(start.timestamp(), end.timestamp()))
