# -*- coding:utf-8 -*-
import smtplib
import email.utils
from email.mime.text import MIMEText
from django.http.request import QueryDict

to_input = lambda str_: 'input-' + str_

def send_notice(data):
    dct = {}
    for key, value in data.items():
        if type(value) == unicode:
            dct[key] = value.encode('utf-8')
        elif type(value) == str:
            pass
        else:
            dct[key] = 'Not support encoding'
    TOPIC = 'Заявка на экскурсию'
    message = [
        'Заявка на экскурсию от ', '', '\n', 'Дата и время: ','','\n',
        'Контактное лицо: ', '', '\n','Телефон: +7', '', '\n', 'Email: ', ''
    ]
    try:
        message[1] = dct[to_input('org')]
        message[4] = dct[to_input('date')] + ' в ' + dct[to_input('time')] + ':00'
        message[7] = dct[to_input('fname')] + ' ' + dct[to_input('lname')]
        message[10] = dct[to_input('tele')]
        message[13] = dct[to_input('email')]
    except KeyError:
        message.append('\nДанные не получены')
    try:
        message = ''.join(message)
    except Exception:
        message = 'Somthing wrong'
    pnztp_user = 'some email'
    pnztp_pwd = 'some password'
    TO = ('some email', 'some email')
    for to in TO:
        msg = MIMEText(message, "", "utf-8")
        msg['To'] = email.utils.formataddr(('Технопарк Яблочков', to))
        msg['From'] = email.utils.formataddr(('Робот pnztp.ru', pnztp_user))
        msg['Subject'] = TOPIC
        tryes = 1
        while tryes < 4:
            try:
                smtpserver = smtplib.SMTP("smtp.mail.ru", 25)
                smtpserver.starttls()
                smtpserver.login(pnztp_user, pnztp_pwd)
                smtpserver.sendmail(pnztp_user, to, msg.as_string())
            except Exception:
                tryes += 1
            else:
                smtpserver.close()
                break