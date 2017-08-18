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

logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
if 'centos' in platform.platform():
    ip_list=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip_list=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging.error("UNKNOWN platform!")
    sys.exit(1)
if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',ip_list.split('\n')[0]):
    endpoint=ip_list.split('\n')[0]+'_'+os.uname()[1]
else:
    logging.error("Get internal ip failed, %s!" %ip.split('\n')[0])
    sys.exit(2)

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
    
