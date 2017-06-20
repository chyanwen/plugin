#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2016.12.08
#Version：1.0
#V1.0 Description：tcp连接状态监控 usage:tcp_conn_status.py

import sys 
import json
import time
import os
import re
import urllib2
import logging
from subprocess import Popen,PIPE
import commands
import platform
import ConfigParser

logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

if 'centos' in platform.platform():
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192\.168|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192\.168|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging.error("UNKNOWN platform!")
    sys.exit(1)

if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',ip.split('\n')[0]):
    endpoint=ip.split('\n')[0]+'_'+os.uname()[1]
else:
    logging.error("Get internal ip failed, %s!" %ip.split('\n')[0])
    sys.exit(2)
#切换目录
try:
    os.chdir(r'/home/work/open-falcon/conf')
except Exception,e:
    logging.error(str(e))
    sys.exit(3)
#判断配置文件是否存在
if not os.path.exists(r'args.conf'):
    logging.error('args.conf is not exists!')
    sys.exit(4)
#获取参数值
port_list=[]
cf = ConfigParser.ConfigParser()
cf.read(r'args.conf')
if 'tcp_conn_status' not in cf.sections():
    logging.error('Config section wrong!')
    sys.exit(9)
for item in cf.items('tcp_conn_status'):
    port_list.append(item[1])
ts=int(time.time())
step=300
counter_list=[]

result=Popen("/usr/sbin/ss -ant",stdout=PIPE,stderr=PIPE,shell=True)
lines=result.stdout.readlines()
for port in port_list:
    sum=0
    tcp_dict={'ESTAB':0,'LISTEN':0,'SYN-RECV':0,'SYN-SENT':0,'TIME-WAIT':0,'CLOSE-WAIT':0,'FIN-WAIT-1':0,'FIN-WAIT-2':0,'LAST-ACK':0,'CLOSED':0,'CLOSING':0}
    for line in lines:
        if re.search(r':%s\s+' % port,line):
            if tcp_dict.has_key(line.split()[0]):
                tcp_dict[line.split()[0]]+=1
            else:
                logging.error("No matched tcp status: %s." %line.split()[0])
    for metric in tcp_dict.keys():
        counter_list.append({ "endpoint": endpoint, "metric": "tcp.%s" % metric.lower(), "timestamp": ts, "step": step, "value": tcp_dict[metric], "counterType": "GAUGE", "tags": "port=%s" % port,})
        sum+=tcp_dict[metric]

    counter_list.append({"endpoint": endpoint, "metric": "tcp.sum", "timestamp": ts, "step": step, "value": sum, "counterType": "GAUGE", "tags": "port=%s" % port,})

print json.dumps(counter_list)
