#!/usr/bin/env python
# encoding=utf8

import datetime
import pdb
import subprocess

import config_file_real

"""
分布式发布脚本

"""


def scp_war(host_arr, app):
    if len(host_arr) == 3:
        account = host_arr[0]
        host = host_arr[1]
        directory = host_arr[2]
        date = datetime.date.today()
        login_info = account + "@" + host
        # bak
        bak_command = "scp -P 22222 " + login_info + ":" + directory + "/webapps/" + app + ".war " + login_info + ":" + directory + "/webapps/" + app + ".war." + str(
            date)
        print(bak_command)
        pdb.set_trace()
        subprocess.check_call(bak_command, shell=True)
        # scp
        print("scp -P 22222 " + "webapps/target/" + app + ".war " + login_info + ":" + directory + "/webapps/")
        subprocess.check_call(
            "scp -P 22222 " + "webapps/target/" + app + ".war " + login_info + ":" + directory + "/webapps/",
            shell=True)


# 需要发布的主机信息
hosts = config_file_real.host
try:
    code = subprocess.check_call(["mvn", "clean", "install", "-Dmaven.test.skip", "-U"])
    if code != 0:
        print(code)
    else:
        # 把war分发到各个服务器
        scp_war(hosts[0], 'elasticsearch')
except subprocess.CalledProcessError as e:
    print(e)
