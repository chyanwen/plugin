#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.06.13
#Version：1.0
#V1.0 Description:监控系统日志打印时间的延迟时间

import os
import time
import json
import commands
import platform
import sys
import logging 
data=[]
logging.basicConfig(level=logging.INFO,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
if 'centos' in platform.platform():
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging.error("UNKNOWN platform!\n")
    sys.exit(1)


#切换目录
try:
    os.chdir(r'/var/log/')
except Exception,e:
    logging.error(str(e))
    sys.exit(3)
try:
    result=commands.getoutput('ls -l --full-time 2>/dev/null| grep messages')
    lines=result.split('\n')
except Exception,e:
    logging.error(str(e))
    sys.exit(3)
for line in lines:
    items=line.split()
    if items[8]=='messages':
        strtime=items[5]+' '+items[6].split('.')[0]
try:
    log_timeArray = time.strptime(strtime, "%Y-%m-%d %H:%M:%S")
except Exception,e:
    logging.error(str(e))
    sys.exit(3)

log_timestamp = time.mktime(log_timeArray)
ts=int(time.time())
delay=ts-int(log_timestamp)

def create_record():
    record = {}
    record['metric'] = 'rsyslog.delay'
    record['endpoint'] = ip.split('\n')[0]+'_'+os.uname()[1]
    record['timestamp'] = ts
    record['step'] = 1800
    record['value'] = delay
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
if data:
   print json.dumps(data)
