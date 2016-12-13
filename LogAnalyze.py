#! /usr/bin/env python2
# -*- coding:utf-8 -*-

"""
计算每种请求的95百分位，99百分位
接口加上请求参数作为同一种请求
"""
import gc
import os
import os.path
import re
import traceback

timeThreshold = 500
resThreshold = 102400
callThreshold = 500
_percentage_95 = 0.95
_percentage_99 = 0.99


def analyzeHttpLog(logDirs):
    countDic = {}
    # timeout = []
    # resToBig = []
    line = ''
    for dir in logDirs:
        for fileName in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, fileName)):
                print(os.path.join(dir, fileName))
                str = ''
                try:
                    fileIn = open(os.path.join(dir, fileName), 'r')
                    while True:
                        line = fileIn.read(20971520)
                        if line == '':
                            break
                        str += line
                except:
                    print(line)
                    traceback.print_exc()
                finally:
                    fileIn.close()
                arr = re.split('\n', str)
                del str
                gc.collect()
                for line in arr:
                    item = analyzeLine(line)
                    if item:
                        key = re.split('\?', item.iname)[0]
                        if key in countDic.keys():
                            countDic[key].append(item)
                        else:
                            countDic[key] = [item]
                            # if int(item.time) > timeThreshold and not item.iname in timeout:
                            # 	timeout.append(item.iname)
                            # if int(item.res) > resThreshold and not item.iname in resToBig:
                            # 	resToBig.append(item.iname)
    printPercentageOff(countDic)


# printTimeOut(timeout)
# printResToBig(resToBig)


def analyzeLine(line):
    if line.rfind(' 200 ') != -1:
        strArr = re.split('[ ]', line)
        if len(strArr) > 0:
            return Item(strArr[-5], strArr[-2], strArr[-1])


class Item:
    """
    每行日志对应一个这种对象,用于计算
    """

    def __init__(self, iname, res, time=0):
        self.iname = iname
        self.res = int(res)
        self.time = int(time)


class Result:
    """
    接口url, 响应时间, 百分位之后的请求
    """

    def __init__(self, name, time, exceptArr):
        self.name = name
        self.time = int(time)
        self.exceptArr = exceptArr


def printPercentageOff(countDic):
    print("打印95,99百分位的请求以及超过部分的异常请求")
    _95Arr = []
    _99Arr = []
    for key in countDic.keys():
        arr = countDic[key]
        sortedArr = sorted(arr, key=lambda item: item.time)
        arrLen = len(sortedArr)
        if arrLen >= callThreshold:
            index95 = calPercentageOff(arrLen, _percentage_95)
            index99 = calPercentageOff(arrLen, _percentage_99)
            _lg95Arr = {}
            _lg99Arr = {}
            for it in sortedArr[index95:]:
                if it.time > timeThreshold:
                    if _lg95Arr.__contains__(it.iname):
                        t = _lg95Arr[it.iname]
                        if t.time < it.time:
                            _lg95Arr[it.iname] = it
                    else:
                        _lg95Arr[it.iname] = it
            for it in sortedArr[index99:]:
                if it.time > timeThreshold:
                    if _lg99Arr.__contains__(it.iname):
                        t = _lg99Arr[it.iname]
                        if t.time < it.time:
                            _lg99Arr[it.iname] = it
                    else:
                        _lg99Arr[it.iname] = it

            _95Arr.append(Result(key, sortedArr[index95 - 1].time, _lg95Arr))
            _99Arr.append(Result(key, sortedArr[index99 - 1].time, _lg99Arr))

    print('打印95百分点以及异常请求')
    printPercentage(_95Arr, '95%')
    print('\n\n\n=======================这是分界线=======================\n\n\n')
    print('打印99百分点以及异常请求')
    printPercentage(_99Arr, '99%')


def printTimeOut(timeout):
    print("根据请求时间打印请求")
    for item in timeout:
        print(item)


def printResToBig(resToBig):
    print("根据响应结果大小打印请求")
    for item in resToBig:
        print(item)


def calPercentageOff(arrLen, percentage):
    return arrLen - int(round(arrLen * (1 - percentage)))


def printPercentage(arr, type):
    for item in arr:
        print(' 请求名称: %s, %s的请求响应时间在%dms以下' % (item.name, type, item.time))
        if type == '99%':
            print(' 响应时间大于%s的异常请求:' % type)
            for it in item.exceptArr:
                print('     请求名称:%s, 响应时间:%d' % (item.exceptArr[it].iname, item.exceptArr[it].time))


if __name__ == '__main__':
    analyzeHttpLog(['/Users/xiuc/Documents/management/analyze_log'])
