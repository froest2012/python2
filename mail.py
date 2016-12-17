#!/bin/bash python
# -*- coding:utf-8 -*-

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from email.header import Header

from_addr = 'search@notice.weichedao.com'
passwd = 'eoKxVIeClc0hsEqQ'
smtp_server = 'smtpdm.aliyun.com'
smtp_port = 25

to_addr_list = ['jiangshou.hong@tqmall.com', 'hang.lou@tqmall.com']
file_path_list = ['/Users/xiuc/Downloads/request_analyze_result.xls',
                  '/Users/xiuc/Downloads/request_analyze_result.xls']
cc = []


def send_mail(send_from, send_to, cc, subject, text, files, smtp_server, port, username='', password='', isTls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ','.join(send_to)
    msg['Cc'] = ','.join(cc)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    for file_path in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file_path, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="' + file_path[file_path.rindex('/') + 1:] + '"')
        msg.attach(part)
    # context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
    # SSL connection only working on Python 3+
    server = smtplib.SMTP(smtp_server, port)
    # server.set_debuglevel(1)
    if isTls:
        server.starttls()
    server.login(username, password)
    server.sendmail(send_from, send_to, msg.as_string())
    server.quit()


if __name__ == '__main__':
    send_mail(from_addr, to_addr_list, cc, Header('测试邮件', 'utf-8').encode(), '测试附件', file_path_list, smtp_server,
              smtp_port, from_addr,passwd, False)
