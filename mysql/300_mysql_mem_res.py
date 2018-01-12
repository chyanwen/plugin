#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Author：yanwen
#Date：2017.05.09
#Version：1.0
#V1.0 Description:监控mysqld的cpu使用率

import os
import sys
import time
import json
import commands
import urllib2
import platform
import logging
import re
from subprocess import Popen,PIPE

endpoint="default"
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

counter_list=[]
ts=int(time.time())
step=300
sum=0.0
result=Popen("top -b -d2 -n5 -w 300| grep -w 'mysqld'|awk '{print $6}'",stdout=PIPE,shell=True)
items=result.stdout.read().split("\n")
for i in range(5):
    if 'g' in items[i]:
        items[i]=float(items[i][:len(items[i])-1])*1024*1024
    elif 'm' in items[i]:
        items[i]=float(items[i][:len(items[i])-1])*1024
    else:
        items[i]=float(items[i])
    sum+=items[i]

value=sum/5
if items!='':
    counter_list.append({"endpoint":endpoint,"metric":"mysql.mem.res","timestamp": ts, "step": step,"value": value, "counterType": "GAUGE", "tags":""})
else:
    logging.error("redis service not start in this server")
    sys.exit(3)
print json.dumps(counter_list)
    
