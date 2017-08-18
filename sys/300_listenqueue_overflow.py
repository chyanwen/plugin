#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.07.22
#Version：1.0
#V1.0 Description：监控收到三次握手ack包，accept队列满
#from subprocess import Popen,PIPE
import os
import time
import json
import commands
import platform
import sys
import logging
data=[]
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

if 'centos' in platform.platform():
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging.error("UNKNOWN platform!\n")
    sys.exit(1)
try:
    result = commands.getoutput("netstat -s | grep overflow |awk '{print $1}'")
    if result=='':
        value=0
    else:
        value=int(result)
except Exception,err:
    logging.error("run command error")
    sys.exit(2)   
def create_record():
    record = {}
    record['metric'] = 'listenqueue.overflow'
    record['endpoint'] = ip.split('\n')[0]+'_'+os.uname()[1]
    record['timestamp'] = int(time.time())
    record['step'] = 300
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
if data:
   print json.dumps(data)
