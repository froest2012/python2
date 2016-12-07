import os, sys
import MySQLdb
import urllib
import json

format = '''{
    "query": {
        "range" : {
            "id" : {
                "gte" : %s,
                "lt" : %s
            }
        }
    },
    "_source":["id", "order_status"]
}
'''

settings = {}
settings['MYSQL_HOST'] = '10.132.27.103'
settings['MYSQL_DBNAME'] = 'legend'
settings['MYSQL_USER'] = 'canal'
settings['MYSQL_PASSWD'] = 'tKh6RI8gH'

db_conn = MySQLdb.connect(host=settings["MYSQL_HOST"],
                          user=settings["MYSQL_USER"],
                          passwd=settings["MYSQL_PASSWD"],
                          port=3306,
                          db=settings["MYSQL_DBNAME"],
                          charset="utf8")


def getIndexStatus(start, count):
	d = {}
	conn = urllib.urlopen(url='http://10.168.103.130:19404/legend_order/_search?size=%s' % count,
	                      data=format % (start, start + count))
	res = json.loads(conn.read())
	for item in res['hits']['hits']:
		fs = item['_source']
		d[fs['id']] = fs['order_status']
	return d


def getDBStatus(start, count):
	global db_conn
	d = {}
	cursor = db_conn.cursor()
	cursor.execute("select id,order_status from legend_order_info where id >= %s and id < %s and is_deleted='N' ",
	               (start, start + count))
	res = cursor.fetchall()
	for item in res:
		d[item[0]] = item[1]
	return d


if __name__ == '__main__':
	# main()
	i = 600000
	count = 1000
	miss = 0
	while i < 690888:
		print 'now:[%s]' % i
		db_map = getDBStatus(i, count)
		es_map = getIndexStatus(i, count)
		if len(db_map) != len(es_map):
			print 'i=[ %s ], len(db)=[%s], len(es)=[%s]' % (i, len(db_map), len(es_map))
		for key in db_map:
			try:
				if (db_map[key] != es_map[key]):
					print 'id=[ %s ], db=[%s], es=[%s]' % (key, db_map[key], es_map[key])
					miss += 1
			except:
				miss += 1
		i += count
	print 'total miss:[%s]' % miss
