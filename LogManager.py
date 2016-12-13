#! /usr/bin/env python2
# -*- coding:utf-8 -*-

"""
管理tomcat的日志
每天的凌晨跑一遍这个日志, 第一个参数是需要整理的日志根目录

-logs/目录只存当天的日志
	-bak/
		-${year-month}/
			-localhost/
			-localhost_access_log/
			-manager/
			-host-manager/
			-catalina/
	localhost.${year-month-day}.log
	localhost_access_log.${year-month-day}.txt
	manager.${year-month-day}.log
	host-manager.${year-month-day}.log
	catalina.${year-month-day}.log
"""

import datetime
import os
import os.path
import re
import shutil
import sys


def manageLogDir(log_dir):
    # 当天日期
    today = datetime.date.today()
    date = re.split('-', str(today))
    log_bak_dir = log_dir + "/bak"
    log_month = log_bak_dir + "/" + date[0] + "-" + date[1]

    # 不存在这个月的文件夹,则创建
    if not os.path.exists(log_month):
        os.makedirs(log_month)

    for file_name in os.listdir(log_dir):
        name_arr = re.split("[.]", file_name)
        if len(name_arr) == 3:
            log_date_arr = re.split("[-]", name_arr[1])
            if log_date_arr and len(log_date_arr) == 3:
                log_date_month = log_date_arr[0] + "-" + log_date_arr[1]

                # 当前文件在bak中对应的目录不存在则创建
                log_file_dir = log_bak_dir + "/" + log_date_month + "/" + name_arr[0]
                if not os.path.exists(log_file_dir):
                    os.makedirs(log_file_dir)

                # 如果文件的日期等于今天得日期, 不移动文件
                # 如果今天得localhost_access_log日志还未生成,并且当前文件的日期是昨天,那么这个文件不移动
                if name_arr[1] == str(today) or (
                        not os.path.exists(log_dir + "/localhost_access_log." + str(today) + ".txt") and name_arr[
                        1] == str(
                            datetime.date.today() + datetime.timedelta(days=-1))):
                    pass
                else:
                    shutil.move(log_dir + "/" + file_name, log_file_dir + "/" + file_name)


if __name__ == '__main__':
    log_dirs = sys.argv[1]
    if log_dirs:
        for log_dir_path in re.split(',', log_dirs):
            manageLogDir(log_dir_path)
