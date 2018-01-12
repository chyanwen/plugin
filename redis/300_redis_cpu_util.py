#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Author：yanwen
#Date：2017.05.09
#Version：1.0
#V1.0 Description:监控redis的cpu使用率

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
result=Popen("top -c -b -d2 -n5 -w 300| grep  'redis-server'|grep -v 'grep' |awk '{sum[$13]+=$9}END{for(i in sum){print i,sum[i]/5} }'",stdout=PIPE,shell=True)
items=result.stdout.readlines()
if len(items)!=0:
    for item in items:
        port=item.split()[0].split(":")[1]
        counter_list.append({"endpoint":endpoint,"metric":"redis.cpu.util","timestamp": ts, "step": step,"value": item.split()[1].split("\n")[0], "counterType": "GAUGE", "tags":"port=%s" %port})
else:
    logging.error("redis service not start in this server")
    sys.exit(3)
print json.dumps(counter_list)
    
