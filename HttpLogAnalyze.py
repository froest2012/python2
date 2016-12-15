#!/bin/bash python
# -*- coding:utf-8 -*-

import re
import sys
from DubboLogAnalyze import DubboLogAnalyze
from DubboLogAnalyze import Item


class HttpLogAnalyze(DubboLogAnalyze):

    def analyze_line(self, line):
        """
        http 请求分析行的方式
        :param line:
        :return:
        """
        global str_arr
        try:
            str_arr = re.split('[ ]', line)
            if len(str_arr) == 12 and str_arr[-3] == '200' and str_arr[-5].find('?') != -1:
                return Item(str_arr[-5][:str_arr[-5].find('?')], int(str_arr[-1][:-1]), int(str_arr[-2]))
        except Exception, e:
            print(e)
            print(str_arr)


if __name__ == '__main__':
    out_file = sys.argv[1]
    bak_dir_name = sys.argv[2]
    http_log_analyze = HttpLogAnalyze()
    http_log_analyze.analyze_log([1, 7, 30], [0.90, 0.95, 0.99], ['/Users/xiuc/Downloads/', '/Users/xiuc/Downloads/'],
                                 out_file,
                                 bak_dir_name, '.log' if bak_dir_name == 'aston-access' else '.txt')
