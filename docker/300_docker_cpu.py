#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2016.12.04
#Version：1.0
#V1.0 Description：docker虚拟机CPU监控
import subprocess
import json
import time
import socket
import commands
import logging
import sys
data=[]
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
re=subprocess.Popen("/usr/bin/sh /home/work/open-falcon/agent/plugin/docker/docker-monitor -c",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
try:
    value=float(re.stdout.readlines()[1].split(':')[1].split()[0])
except Exception,err:
    logging.error("Run command failed:%s" %str(err))
    sys.exit(1)
        
def create_record(value):
    record={}
    record['metric'] = 'docker.cpu'
    record['endpoint'] = ip.split('\n')[0]+'_'+socket.gethostname()
    record['timestamp'] = int(time.time())
    record['step'] = 300
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record(value)
if data:
   print json.dumps(data)
