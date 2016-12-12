#!/bin/bash python
# -*- coding:utf-8 -*-

"""
分析商品查询日志, 获取含有数字,字母的query, 取top200
"""

import os
import os.path
import datetime
import re
from urllib import unquote

result = {}


def contain_digit_or_letter(sub_str):
	for ch in sub_str.decode('utf-8'):
		if u'\u4e00' <= ch <= u'\u9fff':
			return False
	return True


def analyze_line(line, result_tmp):
	if line.find('goods/convert?') != -1:
		start = line.find('q=')
		end = line.find('&', start)
		if start != -1 and end != -1:
			sub_str = line[start + 2:end]
			sub_str = unquote(sub_str)
			if contain_digit_or_letter(sub_str):
				if not result_tmp.__contains__(sub_str):
					result_tmp[sub_str] = 1
				else:
					result_tmp[sub_str] += 1


def print_top_200():
	res = sorted(result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
	if len(res) > 200:
		res = res[:200]
	for item in res:
		print(item[0])


def read_file(file_path, result_tmp):
	with open(file_path, 'r') as f:
		for line in f:
			analyze_line(line, result_tmp)


def _top_200_query(log_dirs):
	i = 0
	while i <= 30:
		date_str = str(datetime.date.today() + datetime.timedelta(days=-i))
		for log_dir in log_dirs:
			file_path = log_dir + '/localhost_access_log.' + date_str + '.txt'
			if os.path.exists(file_path) and os.path.isfile(file_path):
				read_file(file_path, result)
			else:
				date_arr = re.split('-', date_str)
				date_tmp = date_arr[0] + '-' + date_arr[1]
				file_name = 'localhost_access_log.' + date_str + '.txt'
				file_path = os.path.join(log_dir + '/bak/' + date_tmp + '/localhost_access_log/', file_name)
				if os.path.exists(file_path) and os.path.isfile(file_path):
					read_file(file_path, result)
		i += 1
	print_top_200()


if __name__ == '__main__':
	_top_200_query(['/Users/xiuc/Downloads', '/Users/xiuc/Downloads'])
