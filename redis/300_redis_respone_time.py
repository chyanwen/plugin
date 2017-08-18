#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.03.28
#Version：1.0
#V1.0 Description：监控redis响应时间，使用：redis_response_time.py port

import sys 
import json
import time
import os
import re
import urllib2
import commands
import platform
import logging
from subprocess import Popen,PIPE

logging.basicConfig(level=logging.ERROR,
                    filename='/home/work/open-falcon/agent/plugin/error.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

if 'centos' in platform.platform():
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging.error("UNKNOWN platform!")
    sys.exit(1)

if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',ip.split('\n')[0]):
    endpoint=ip.split('\n')[0]+'_'+os.uname()[1]
else:
    logging.error("Get internal ip failed, %s!" %ip.split('\n')[0])
    sys.exit(2)

endpoint=ip.split('\n')[0]+'_'+os.uname()[1]
port_list=[]
ts=int(time.time())
step=300
counter_list=[]
value = 0
port_text=commands.getoutput("ps -ewwf | grep redis-server | grep -v grep | awk '{print $9}'")
if port_text!='':
    for port in port_text.split("\n"):
        port_list.append(port.split(":")[1])
else:
   logging.error("redis service not start in this server!")
   sys.exit(3)
    
def sys_command_outstatuserr(cmd, timeout=3):
    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        errmsg=p.stderr.readlines()
        if len(errmsg)!=0:
            logging.error(errmsg)
            sys.exit(6)
    except Exception,e:
        logging.error("run command %s error!" %cmd)
        sys.exit(5)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            if p.poll()!=0:
                return timeout
            else:
                seconds_passed = time.time() - t_beginning
                return seconds_passed
        seconds_passed = time.time() - t_beginning
	if timeout and seconds_passed > timeout:
            p.terminate()
            return seconds_passed
        time.sleep(0.01)

for port in port_list:
    response_time=sys_command_outstatuserr("redis-cli -p %s ping " %port)
    counter_list.append({"endpoint":endpoint,"metric":"redis.response_time","timestamp": ts, "step": step, "value": response_time, "counterType": "GAUGE", "tags": "port=%s" % port,})
print json.dumps(counter_list)
