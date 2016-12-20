#!/bin/bash python2
# -*- coding:utf-8 -*_

import os
import os.path
import json
import sys
import xlwt
import datetime
import mail
from email.header import Header
import traceback


from_addr = 'xxxx'
passwd = 'xxxx'
smtp_server = 'xxxx'
smtp_port = 25
to_addr_list = ['xxx']
file_path_list = []
cc = []


def merge_res_dict(result_dic, file_dic):
    for key in file_dic:
        res_item = file_dic[key]
        if not result_dic.get(key):
            result_dic[key] = res_item
        else:
            it = result_dic[key]
            for line_key in res_item:
                line_item = res_item[line_key]
                if not it.get(line_key):
                    it[line_key] = line_item
                else:
                    it_item = it[line_key]
                    for attr_key in line_item:
                        if attr_key == '_1latency':
                            it_item[attr_key] = str((int(it_item[attr_key][:-2]) + int(line_item[attr_key][:-2])) / 2) + 'ms'
                        elif attr_key == '_0count':
                            it_item[attr_key] = it_item[attr_key] + line_item[attr_key]
                        elif attr_key == '_2res':
                            it_item[attr_key] = (it_item[attr_key] + line_item[attr_key]) / 2
                        else:
                            if it_item[attr_key] < line_item[attr_key]:
                                it_item[attr_key] = line_item[attr_key]


def read_files(dir_path):
    result_dic = {}
    if os.path.exists(dir_path):
        json_reader = json.JSONDecoder(object_hook=byteify)
        for file_path in os.listdir(dir_path):
            ss = open(os.path.join(dir_path, file_path), 'r').read()
            file_dic = json_reader.decode(ss)
            merge_res_dict(result_dic, file_dic)
    return result_dic


def sort_result(result_dic):
    return sorted(result_dic.items(), lambda x, y: cmp(x[1]['30']['_0count'], y[1]['30']['_0count']), reverse=True)


def byteify(input):
    """
    json读取文件中的字典, 字符串会变成unicode, 用这个方法作为object_hook来把每个字符串转成utf-8编码
    :param input:
    :return:
    """
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def save_to_xls(res_tmp, file_path):
    xls = xlwt.Workbook(encoding='utf-8')
    _sheet = xls.add_sheet('所有请求汇总分析')
    header = ['请求名称', '', '调用次数', 'latency(ms)', '返回结果大小', '90百分点', '95百分点(ms)', '99百分点(ms)']
    i = 0
    for head in header:
        _sheet.write(0, i, head)
        i += 1
    # 填数据
    _0cell_max_width = 0
    i = 1
    for _3line in res_tmp:
        j = 0
        iname = _3line[0]
        cal_max_width(_sheet, j, _0cell_max_width, iname)
        _sheet.write_merge(i, i + 2, 0, j, iname, request_name_style())
        j += 1
        k = 0
        sub_lines = sorted(_3line[1].items(), key=lambda x: int(x[0]))
        k += 3 - len(sub_lines)
        for _line_key in sub_lines:
            m = 0
            _sheet.write(i + k, j + m, _line_key[0])
            m += 1
            line_tmp = _line_key[1].items()
            line_tmp.sort()
            for item_key in line_tmp:
                _sheet.write(i + k, j + m, item_key[1])
                m += 1
            k += 1
        i += 3
    xls.save(file_path)


def cal_max_width(_sheet, j, max_now, str_name):
    if len(str_name) * 630 > max_now:
        max_now = len(str_name) * 630
        _sheet.col(j).width = max_now


def font_bold_style():
    font = xlwt.Font()
    font.bold = True
    return font


def alignment_style():
    alignment = xlwt.Alignment()
    alignment.horz = alignment.HORZ_LEFT
    alignment.vert = alignment.VERT_CENTER
    return alignment


def request_name_style():
    style = xlwt.XFStyle()
    style.font = font_bold_style()
    style.alignment = alignment_style()
    return style


def save_res(res_tmp, save_res_path):
    """
    把每天的分析结果保存到文件, 以便日后分析统计
    :param res_tmp:
    :param save_res_path:
    :return:
    """
    json_write = json.JSONEncoder()
    with open(os.path.join(save_res_path, 'log_analyze_res.' + str(datetime.date.today())) + '.log', 'w') as f:
        f.write(json_write.encode(res_tmp))


if __name__ == '__main__':
    try:
        files_dir = sys.argv[1]
        file_path = sys.argv[2]
        save_res_path = sys.argv[3]
        result_dic = read_files(files_dir)
        res_tmp = sort_result(result_dic)
        save_res(res_tmp, save_res_path)
        file_name = file_path + '.' + str(datetime.date.today()) + '.xls'
        save_to_xls(res_tmp, file_name)
        file_path_list.append(file_name)
        mail.send_mail(from_addr, to_addr_list, cc, Header('搜索请求日志分析报告' + str(datetime.date.today()), 'utf-8').encode(), '', file_path_list, smtp_server, smtp_port, from_addr, passwd, False)
    except Exception, e:
        print(e)
        traceback.print_exc()


