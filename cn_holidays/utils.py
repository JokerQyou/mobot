# coding: utf-8
from datetime import datetime
import io
import os.path
import sys

import enum
import pytz

if sys.version_info.major < 3:
    from backports import csv
else:
    import csv

DATA_FIELDS = [
    'name', 'date', 'description', 'observed', 'isholiday', 'isworkday',
]
CACHE = {}
TZ = pytz.timezone('Asia/Shanghai')


@enum.unique
class DAY_TYPES(enum.Enum):
    WORKDAY = 0
    WEEKEND = 1
    HOLIDAY = 2
    HOLIDAY_TRADEOFF = 3


def clean_up_dict(d):
    '''
    Cleanup dict values
    '''
    r = {}
    for k, v in d.items():
        if isinstance(k, basestring):
            key = k.strip()
        if isinstance(v, basestring):
            value = v.strip()
        r[key] = value
    return r


def load_data(year):
    '''
    Load data into memory cache
    '''
    year = str(year)
    if year in CACHE:
        return True

    data_file = os.path.join(
        os.path.dirname(__file__), 'data', '{}.csv'.format(year)
    )
    if not os.path.isfile(data_file):
        return False

    CACHE[year] = {}
    with io.open(data_file, encoding='utf-8') as rf:
        # Detect CSV header line
        has_header = csv.Sniffer().has_header(rf.read(1024))
        rf.seek(0)

        reader = csv.DictReader(rf, DATA_FIELDS)
        if has_header:
            next(reader)

        for data_line in reader:
            day = clean_up_dict(data_line)
            # Convert into `int` type so we don't need to parse it afterwards
            dt = datetime.strptime(day['date'], '%Y-%m-%d')
            day['year'] = dt.year
            day['month'] = dt.month
            day['day'] = dt.day
            day['isholiday'] = bool(int(day['isholiday']))
            day['isworkday'] = bool(int(day['isworkday']))
            CACHE[year][day.pop('date')] = day

    return True


def get_day_type(dt):
    '''Return type of given date'''
    # Naive time => localized time
    if dt.tzinfo is None:
        dt = TZ.localize(dt)
    else:
        # Timezone correction
        dt = TZ.normalize(dt)

    year = str(dt.year)
    load_data(year)
    matched_days = filter(
        lambda x: all([
            x['year'] == dt.year,
            x['month'] == dt.month,
            x['day'] == dt.day,
        ]),
        CACHE[year].values()
    )
    if filter(lambda x: x['isholiday'] is True, matched_days):
        return DAY_TYPES.HOLIDAY

    if filter(lambda x: x['isworkday'] is True, matched_days):
        return DAY_TYPES.HOLIDAY_TRADEOFF

    if dt.weekday() > 4:
        return DAY_TYPES.WEEKEND

    return DAY_TYPES.WORKDAY


def is_workday(dt):
    '''
    Detect if given datetime is a workday.
    These are not workdays:
    - Weekends (`dt.weekday() > 4`);
    - Holidays (as defined from data files);
    If given date is defined as holiday tradeoff, it is indeed a workday.
    '''
    day_type = get_day_type(dt)
    return day_type is DAY_TYPES.WORKDAY\
        or day_type is DAY_TYPES.HOLIDAY_TRADEOFF
