#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2016.12.04
#Version：1.0
#V1.0 Description：corefile文件监控

from subprocess import Popen,PIPE
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

if os.path.exists('/home/corefile'):
    value = len(os.listdir('/home/corefile'))
elif os.path.exists('/var/corefile'):
    value = len(os.listdir('/var/corefile'))
else:
    value=0

def create_record():
    record = {}
    record['metric'] = 'check.corefile'
    record['endpoint'] = endpoint
    record['timestamp'] = int(time.time())
    record['step'] = 600
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
if data:
   print json.dumps(data)
