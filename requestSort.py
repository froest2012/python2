#! /usr/bin/python2
# -*- coding:utf-8 -*-

import re

requestFile = open('/Users/xiuc/Documents/management/search/tmp', 'r')
line = ''
requestDic = {}
while True:
	line = requestFile.readline()
	if line == '':
		break
	strArr = re.split('[ ]', line)
	requestDic[strArr[0]] = int(strArr[1])
sortedDics = sorted(requestDic.items(), key=lambda item: item[1], reverse=True)
for item in sortedDics:
	print("%s %d" % (item[0], item[1]))
