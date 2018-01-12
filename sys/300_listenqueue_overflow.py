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
endpoint="default"
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

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
    record['endpoint'] = endpoint
    record['timestamp'] = int(time.time())
    record['step'] = 300
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
if data:
   print json.dumps(data)
