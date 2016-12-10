#! /usr/bin/env python2
# -*- coding:utf-8 -*-

"""
统计类型:
	前一天:
		接口请求数
		latency, 该接口所有调用时间总和的平均时间
		90百分位
		95百分位
		99百分位
		...
	7天:
		接口请求数
	30天:
		接口请求数
	...
"""
import re
import os
import os.path
import datetime

_percentage_90 = 0.90
_percentage_95 = 0.95
_percentage_99 = 0.99
result = {}


def analyze_log(days, percentage_arr, log_dirs):
	"""
	:param days:        需要统计的天数
	:param percentage_arr:  需要计算的百分位
	:param log_dirs:    日志文件根路径
	:return:
	"""
	count_dic = {}
	days = sorted(days)
	i = 1
	while i <= days[-1]:
		date_arr = re.split("-", str(datetime.date.today() + datetime.timedelta(days=-i)))
		file_name = 'aston-access.' + "-".join(date_arr) + '.log'
		file_path = os.path.join(log_dirs, file_name)
		if os.path.exists(file_path) and os.path.isfile(file_path):
			read_file(log_dirs, file_name, count_dic)
			print(file_path)
		else:
			date_tmp = date_arr[0] + '-' + date_arr[1]
			file_path = os.path.join(log_dirs + '/bak/' + date_tmp, file_name)
			if os.path.exists(file_path) and os.path.isfile(file_path):
				read_file(log_dirs + '/bak/' + date_tmp, file_name)
				print(file_path)
		if days.__contains__(i):
			# 计算一次
			cal_result_item(count_dic, i, percentage_arr, result)
		i += 1
	print_result()


def read_file(dir_name, file_name, count_dic):
	"""
	从文件一行行读入数据, 并分析每一行, 最后存到字典中
	:param dir_name:    文件夹路径
	:param file_name:   文件名
	:param count_dic:   结果字典
	:return:
	"""
	with open(os.path.join(dir_name, file_name), 'r') as f:
		for line in f:
			item = analyze_line(line)
			if item:
				key = item.iname
				time_arr = []
				if count_dic.__contains__(key):
					it = count_dic[key]
					time_arr = it[2]
					time_arr.append(item.time)
					count_dic[key] = (it[0] + item.time, it[1] + 1, time_arr)  # (time, count, list)
				else:
					time_arr.append(item.time)
					count_dic[key] = (item.time, 1, time_arr)


def analyze_line(line):
	"""
	分析每一行数据,得到一个item
	:param line:
	:return:
	"""
	if line.rfind(' success ') != -1:
		str_arr = re.split('[ ]', line)
		if len(str_arr) > 0:
			return Item(str_arr[8], str_arr[9][:-2])


class Item:
	"""
	每行日志对应一个这种对象,用于计算
	"""

	def __init__(self, iname, time=0):
		"""
		:param iname:   接口名称
		:param time:    响应时间
		:return:
		"""
		self.iname = iname
		self.time = int(time)


def cal_result_item(count_dic, n, percentage_arr, result_dic):
	"""
	计算latency, 调用总数, 百分位
	:param count_dic:       结果字典
	:param n:               分析n天前的数据
	:param percentage_arr:  需要计算的百分位数组
	:param result_dic:      结果字典
	:return:
	"""
	for key in count_dic.keys():
		latency = count_dic[key][0] / count_dic[key][1]
		count = count_dic[key][1]
		arr = count_dic[key][2]
		sorted_arr = sorted(arr)
		arr_len = len(sorted_arr)
		line = {'name': key, 'latency': latency, 'count': count}
		for x in percentage_arr:
			index = cal_percentage_off(arr_len, x)
			line[get_percentage_key(x)] = sorted_arr[index - 1]
		key_line = {}
		if result_dic.__contains__(key):
			key_line = result_dic[key]
		key_line[n] = line
		result_dic[key] = key_line


def cal_percentage_off(arr_len, percentage):
	"""
	计算百分位在该数组中的位置
	:param arr_len:     数组
	:param percentage:  需要计算的百分位
	:return:
	"""
	return arr_len - int(round(arr_len * (1 - percentage)))


def print_result():
	"""
	打印最终结果result
	:return:
	"""
	pass


def get_percentage_key(x):
	"""
	计算百分位对应在字典中的key, 例: "_95"
	:param x:
	:return:
	"""
	return '_' + str(int(x * 100))


if __name__ == '__main__':
	analyze_log([1, 7, 30, 35], [0.90, 0.95, 0.97, 0.99], '/Users/xiuc/Downloads/')
