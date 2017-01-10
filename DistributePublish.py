#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import pdb
import sys
import os
import subprocess
import xmlrpclib
import importlib

"""
分布式发布脚本

"""
# 如果valid='valid',则只发布服务器列表中的第一个机器，否则发布所有服务器
valid = 'valid'
config_env = ''
if len(sys.argv) == 3:
    config_env = sys.argv[1]
    valid = sys.argv[2]


def copy_config(antx_env):
    config_folder = '../antx_env/' + antx_env
    the_config_file_py = config_folder + '/config_file.py'
    the_antx_properties_file = config_folder + '/antx.properties'
    os.system('cp ' + the_config_file_py + ' ./bin/config_file_real.py')
    os.system('cp ' + the_antx_properties_file + ' ./')


copy_config(config_env)
config_file_real = importlib.import_module('config_file_real')
hosts = config_file_real.host


def scp_war(host_arr, war_name, app):
    if len(host_arr) == 5:
        account = host_arr[0]
        host = host_arr[1]
        directory = host_arr[2]
        server = xmlrpclib.Server('http://' + host + ':9001/RPC2')
        date = datetime.date.today()
        login_info = account + "@" + host
        app_file_dir = directory + '/webapps'
        waiting_bak_file = app_file_dir + '/' + war_name + '.war'
        bak_file = app_file_dir + '/' + war_name + '.war.' + str(date)
        command = "scp -P 22222 " + "webapp/target/" + war_name + ".war " + login_info + ":" + directory
        print(command)
        subprocess.check_call(command, shell=True)
        print('backup ' + waiting_bak_file + ' to ' + bak_file)
        server.xiuc.move_file(waiting_bak_file, bak_file)
        print('move ' + directory + '/' + war_name + '.war to ' + waiting_bak_file)
        server.xiuc.move_file(directory + '/' + war_name + '.war', waiting_bak_file)
        print('rm project dir in webapps:' + app_file_dir + '/' + war_name)
        server.xiuc.sysexec('rm -rf ' + app_file_dir + '/' + war_name)
        try:
            print('stop running app:' + app)
            if server.supervisor.stopProcess(app):
                print('restart app:' + app)
                server.supervisor.startProcess(app)
        except Exception as e:
            print('app was not running, starting app:' + app + ' directly')
            server.supervisor.startProcess(app)
    return True


try:
    code = subprocess.check_call(["mvn", "clean", "install", "-Dmaven.test.skip", "-U"])
    if code != 0:
        print(code)
    else:
        # 把war分发到各个服务器
        # pdb.set_trace()
        if valid == 'valid':
            scp_war(hosts[0], hosts[0][4], hosts[0][3])
        elif valid == 'valid':
            for item in hosts:
                scp_war(item, item[4], item[3])
except subprocess.CalledProcessError as e:
    print(e)
