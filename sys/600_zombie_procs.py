#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2016.12.04
#Version：1.0
#V1.0 Description：僵尸进程数监控监控

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
    logging.error("UNKNOWN platform!")
    sys.exit(1)
#def getvalue():
#    re=Popen("ps -aux | awk '{print $8}' | grep '^Z$' |wc -l",stdout=PIPE,stderr=PIPE,shell=True)
#    return int(re.communicate()[0].strip())
try:
    value = int(commands.getoutput("ps -aux | awk '{print $8}' | grep '^Z$' |wc -l").strip())
except Exception,err:
    logging.error("Run command failed:%s" %str(err))
    sys.exit(2)
def create_record():
    record = {}
    record['metric'] = 'zombie.procs'
    record['endpoint'] = ip.split('\n')[0]+'_'+os.uname()[1]
    record['timestamp'] = int(time.time())
    record['step'] = 600
    record['value'] = value
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
if data:
   print json.dumps(data)
