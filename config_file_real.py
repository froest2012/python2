#!/usr/bin/env python
# encoding=utf8
"""
可以添加多组服务器,用列表的形式

每组有5个属性: 账户名称, 服务器ip, tomcat路径, supervisor管理的应用节点名称, 服务war包名
"""
# 测试环境
host = [
    ['tqmall.es', '10.160.16.177', '/data/es_server/tomcat', 'tomcat', 'elasticsearch']
]
