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

	脚本调用方式: python script out_file log_file_name, protocl
"""

import datetime
import os
import os.path
import re
import sys
import json

result = {}

class Item:
        """
        每行日志对应一个这种对象,用于计算
        """

        def __init__(self, iname, time=0, res=0):
            """
            :param iname:   接口名称
            :param time:    响应时间
            :return:
            """
            self.iname = iname
            self.time = int(time)
            self.res = int(res)

class DubboLogAnalyze(object):

    def analyze_log(self, days, percentage_arr, log_dirs, out_file, bak_dir_name, suffix):
        """
        分析日志
        :param bak_dir_name:
        :param days:
        :param percentage_arr:
        :param log_dirs:
        :param out_file:
        :return:
        """
        count_dic = {}
        days = sorted(days)
        i = 1
        while i <= days[-1]:
            for dir_tmp in log_dirs:
                date_arr = re.split("-", str(datetime.date.today() + datetime.timedelta(days=-i)))
                file_name = bak_dir_name + '.' + "-".join(date_arr) + suffix
                file_path = os.path.join(dir_tmp, file_name)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    self.read_file(dir_tmp, file_name, count_dic)
                    print(file_path)
                else:
                    date_tmp = date_arr[0] + '-' + date_arr[1]
                    file_path = os.path.join(dir_tmp + '/bak/' + date_tmp + '/' + bak_dir_name + '/', file_name)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        self.read_file(dir_tmp + '/bak/' + date_tmp + '/' + bak_dir_name + '/', file_name,
                                       count_dic)
                        print(file_path)
            if days.__contains__(i):
                # 计算一次
                self.cal_result_item(count_dic, i, percentage_arr, result)
            i += 1
        self.save_result_to_file(result, out_file)
        # print_result(result, days[-1], out_file)

    def read_file(self, dir_name, file_name, count_dic):
        """
        从文件一行行读入数据, 并分析每一行, 最后存到字典中
        :param dir_name:    文件夹路径
        :param file_name:   文件名
        :param count_dic:   结果字典
        :return:
        """
        with open(os.path.join(dir_name, file_name), 'r') as f:
            for line in f:
                item = self.analyze_line(line)
                if item:
                    key = item.iname
                    time_arr = []
                    if count_dic.__contains__(key):
                        it = count_dic[key]
                        time_arr = it[2]
                        time_arr.append(item.time)
                        count_dic[key] = (
                            it[0] + item.time, it[1] + 1, time_arr, it[3] + item.res)  # (time, count, list)
                    else:
                        time_arr.append(item.time)
                        count_dic[key] = (item.time, 1, time_arr, item.res)

    def analyze_line(self, line):
        """
        分析每一行数据,得到一个item
        :param line:
        :return:
        """
        str_arr = re.split('[ ]', line)
        if len(str_arr) > 0:
            return Item(str_arr[8], str_arr[9][:-2], str_arr[11])

    def cal_result_item(self, count_dic, n, percentage_arr, result_dic):
        """
        计算latency, 调用总数, 百分位
        :param count_dic:       结果字典
        :param n:               分析n天前的数据
        :param percentage_arr:  需要计算的百分位数组
        :param result_dic:      结果字典
        :return:
        """
        for key in count_dic.keys():
            count = count_dic[key][1]
            latency = count_dic[key][0] / count
            res_size = count_dic[key][3] / count
            arr = count_dic[key][2]
            sorted_arr = sorted(arr)
            arr_len = len(sorted_arr)
            line = {'_1latency': str(latency) + 'ms', '_0count': count, '_2res': res_size}
            for x in percentage_arr:
                index = self.cal_percentage_off(arr_len, x)
                line[self.get_percentage_key(x)] = sorted_arr[index - 1]
            key_line = {}
            if result_dic.__contains__(key):
                key_line = result_dic[key]
            key_line[n] = line
            result_dic[key] = key_line

    def cal_percentage_off(self, arr_len, percentage):
        """
        计算百分位在该数组中的位置
        :param arr_len:     数组
        :param percentage:  需要计算的百分位
        :return:
        """
        return arr_len - int(round(arr_len * (1 - percentage)))

    def save_result_to_file(self, result_param, out_f):
        """
        把排序以后的元组写入文件,用于多个文件的合并再排序,然后生成xls
        :param result_param:
        :param n:
        :param out_f:
        :return:
        """
        file_tmp = open(out_f, 'w')
        # res = sorted(result_param.items(), lambda x, y: cmp(x[1][n]['_0count'], y[1][n]['_0count']), reverse=True)
        json_writer = json.JSONEncoder()
        file_tmp.write(json_writer.encode(result_param))
        file_tmp.close()

    def print_result(self, result_param, n, out_f):
        """
        打印最终结果result
        :param result_param:    结果参数
        :param n:               按照n天的数据字典中的count降序排序
        :param out_f:
        :return:
        """
        file_tmp = open(out_f, 'w')
        res = sorted(result_param.items(), lambda x, y: cmp(x[1][n]['_0count'], y[1][n]['_0count']), reverse=True)
        for item in res:
            line_arr = [item[0]]
            item_tmp = item[1].items()
            item_tmp.sort()
            for tmp in item_tmp:
                line_arr.append(str(tmp[0]) + ':')
                line_item = tmp[1]
                line_tmp = line_item.items()
                line_tmp.sort()
                for it in line_tmp:
                    line_arr.append(it[1])
            line_arr.append('\n')
            file_tmp.write(' '.join(str(x) for x in line_arr))
        json_writer = json.JSONEncoder()
        # file_tmp.write(json_writer.encode(result_param))
        file_tmp.close()

    def get_percentage_key(self, x):
        """
        计算百分位对应在字典中的key, 例: "_95"
        :param x:result_param
        :return:
        """
        return '_' + str(int(x * 100))


if __name__ == '__main__':
    out_file = sys.argv[1]
    bak_dir_name = sys.argv[2]
    dubbo_log_analyze = DubboLogAnalyze()
    dubbo_log_analyze.analyze_log([1, 7, 30], [0.90, 0.95, 0.99], ['/Users/xiuc/Downloads/', '/Users/xiuc/Downloads/'],
                                  out_file,
                                  bak_dir_name, '.log' if bak_dir_name == 'aston-access' else '.txt')
