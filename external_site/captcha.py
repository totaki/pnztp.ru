# -*- coding:utf-8 -*-
import urllib
import xml.etree.ElementTree as ET


def get_yandex_captcha():
    KEY = 'some key'

    id_ = urllib.urlopen('http://cleanweb-api.yandex.ru/1.0/check-spam?key=%s' % KEY).read()
    id_ = ET.fromstring(id_)
    try:
        id_ = (i.text for i in id_ if i.tag == 'id').next()
    except StopIteration:
        pass
    captcha = urllib.urlopen('http://cleanweb-api.yandex.ru/1.0/get-captcha?key=%s&id=%s' % (KEY, id_)).read()
    captcha = ET.fromstring(captcha)
    try:
        iter_ = ([i.tag, i.text] for i in captcha if i.tag == 'captcha' or i.tag == 'url')
        captcha = {'id': id_}
        for i in iter_:
            captcha[i[0]] = i[1]
    except StopIteration:
        pass
    return captcha


def check_yandex_captcha(id_, captcha, value):
    KEY = 'some key'

    values = urllib.urlencode({'key': KEY, 'id': id_, 'captcha': captcha, 'value': value})
    check = urllib.urlopen('http://cleanweb-api.yandex.ru/1.0/check-captcha?%s' % values).read()
    check = ET.fromstring(check)
    try:
        check = (i.tag for i in check if i.tag == 'ok' or i.tag == 'failed').next()
    except StopIteration:
        pass
    return (lambda x: True if x == 'ok' else False)(check)