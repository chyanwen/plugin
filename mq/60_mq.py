#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import json
import time
import logging
import urllib2
import re

logging.basicConfig(level=logging.ERROR,
                    filename='/home/work/open-falcon/agent/plugin/error.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
endpoint='default'
step=60
ts=int(time.time())
counter_list=[]
queue_flag=0
queue={}
tmp_queue=''
ip='127.0.0.1'
broker={'Store_percent_used':0,'Memory_percent_used':0,'Temp_percent_used':0}
broker_flag=0

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

url_queue='http://%s:8161/admin/queues.jsp' %ip
url_index='http://%s:8161/admin/index.jsp' %ip
try:
    res=urllib2.urlopen(url_queue,timeout=3)
    res1=urllib2.urlopen(url_index,timeout=3)
except urllib2.HTTPError,ex:
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None,url_queue,'admin','admin')
    password_mgr.add_password(None,url_index,'admin','admin')
    handler=urllib2.HTTPBasicAuthHandler(password_mgr)
    opener=urllib2.build_opener(handler)
    try:
        res=opener.open(url_queue,timeout=3)
        res1=opener.open(url_index,timeout=3)
    except Exception,err:
        logging.error('Request mq error,ip:%s!' %ip)
        sys.exit(1)
except Exception,err:
    logging.error('Request mq error,ip:%s!' %ip)
    sys.exit(1)

for line in res.readlines():
    if re.match(r'^[a-zA-Z].*</a></td>',line):
        tmp_queue=line.split('<')[0]
        queue_flag=1
    elif queue_flag:
        queue[tmp_queue]=int(line.split('<td>')[1].split('</td>')[0])
        queue_flag=0
        tmp_queue=''

for line in res1.readlines():
    if 'Store percent used' in line: 
        broker_flag=1
    elif 'Memory percent used' in line: 
        broker_flag=2
    elif 'Temp percent used' in line:
        broker_flag=3
    elif broker_flag==1:
        broker['Store_percent_used']=int(line.split('<b>')[1].split('</b>')[0])
        broker_flag=0
    elif broker_flag==2:
        broker['Memory_percent_used']=int(line.split('<b>')[1].split('</b>')[0])
        broker_flag=0
    elif broker_flag==3:
        broker['Temp_percent_used']=int(line.split('<b>')[1].split('</b>')[0])
        broker_flag=0


for key,value in queue.items():
    counter_list.append({"endpoint":endpoint,"metric":"mq.status","tags":"mq=%s" %key,"timestamp":ts,"step":step,"counterType":"GAUGE","value":value})

for key,value in broker.items():
    counter_list.append({"endpoint":endpoint,"metric":"mq.status.%s" %key,"tags":"","timestamp":ts,"step":step,"counterType":"GAUGE","value":value})

print json.dumps(counter_list)
