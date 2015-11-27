# -*- coding:utf-8 -*-
import json
import re
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from external_site.captcha import get_yandex_captcha, check_yandex_captcha
from external_site.myemail import send_notice


MONTHS = {
  1: 'Январь',
  2: 'Февраль',
  3: 'Март',
  4: 'Апрель',
  5: 'Май',
  6: 'Июнь',
  7: 'Июль',
  8: 'Август',
  9: 'Сентябрь',
  10: 'Октябрь',
  11: 'Ноябрь',
  12: 'Декабрь'
}

WORK_HOURS = (10,11,13,14)
WORK_DAYS = (1,2,3,4,5)
WORK = 1
NOT_WORK = 2
CAPTCHA = 'captcha'
INPUT = 'input-'


c_date = lambda: datetime.today()


def _get_month_days(date_):
    while (date_ + timedelta(1)).day != 1:
        date_ = date_ + timedelta(1)
    for i in range(1, date_.day + 1):
        yield i


def _get_weeks(c_day, days, offset):
    week_day = 1 + len(offset)
    weeks = [[]]
    for day in days:
        weeks[-1].append([day, week_day in WORK_DAYS and day > c_day])
        if week_day == 7:
            weeks.append([])
            week_day = 0
        week_day += 1
    return weeks


def get_calendar(date_):
    info = {}
    info['month'] = (MONTHS[date_.month], date_.month)
    info['offset'] = []
    for i in range(0, date(date_.year, date_.month, 1).weekday()):
        info['offset'].append(False)
    info['days'] =  _get_month_days(date_)
    info['weeks'] = _get_weeks(date_.day, info['days'], info['offset'])
    return info


def get_two_month(date_):
    info = []
    info.append(get_calendar(date_))
    next_date = date(
        (lambda: date_.year + 1 if date_.month == 12 else date_.year)(),
        (lambda: 1 if date_.month == 12 else date_.month + 1)(),
        1
    )
    info.append(get_calendar(next_date))
    return info


_regexs = {
    'org': u'^[a-zA-Zа-яА-Я0-9 ]{1,100}$',
    'date': r'^(\d\d?.\d\d?)$',
    'time': r'^(10|11|13|14)$',
    'clients': r'^(<10|10-20|20-30|30-40|40-50)$',
    'fname': u'^[a-zA-Zа-яА-Я]{1,20}$',
    'lname': u'^[a-zA-Zа-яА-Я]{1,20}$',
    'tele': r'^\(\d{3,4}\)\d{2,3}-\d{2}-\d{2}$',
    CAPTCHA: r'^(\d+)$'
}


def _check_email(string):
    try:
        validate_email(string)
    except ValidationError:
        return False
    else:
        return string


def _check_input(key, value):
    if bool(re.match(_regexs[key], value)):
        return value
    return False

  
def _check_captcha(data, dct):
    check = check_yandex_captcha(
        data[CAPTCHA + '-id'], data[CAPTCHA], data[INPUT + CAPTCHA]
    )
    if check:
        
        return {'captcha': True}
    else:
        return {'captcha': False}


def checker(data):
    slc = lambda str_: str_[len(INPUT):]
    dct = {}
    try:
        for i in data.keys():
            if slc(i) == 'email':
                dct[slc(i)] = _check_email(data[i])
            elif i.startswith(CAPTCHA):
              continue
            else:
                dct[slc(i)] = _check_input(slc(i), data[i])
        if CAPTCHA in data:
            dct = _check_captcha(data, dct)
            if dct[CAPTCHA]:
                send_notice(data)
        dct = json.dumps(dct)
    except ValueError:
        dct = json.dumps({'error': True})
    finally:
        return dct