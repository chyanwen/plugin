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
result=Popen("top -b -d2 -n5 -w 300| grep -w 'mysqld'|awk '{sum[$12]+=$9}END{for(i in sum){print i,sum[i]/5} }'",stdout=PIPE,shell=True)
item=result.stdout.read().split("\n")[0]
if item!='':
    counter_list.append({"endpoint":endpoint,"metric":"mysql.cpu.util","timestamp": ts, "step": step,"value": item.split()[1], "counterType": "GAUGE", "tags":""})
else:
    logging.error("redis service not start in this server")
    sys.exit(3)
print json.dumps(counter_list)
    
