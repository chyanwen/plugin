#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.03.15
#Version：1.0
#V1.0 Description：监控docker服务是否开启及docker可用磁盘空间

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
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192\.168|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192\.168|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging("UNKNOWN platform!")
    sys.exit(1)
def getvalue():
    value = 0
    try:
        status=int(commands.getoutput("which docker >/dev/null 2>&1;echo $?"))
    except Exception,err:
        logging.error("Run command failed:%s" %str(err))
        sys.exit(2)
    if status == 0:
        Available = commands.getoutput("/usr/bin/docker info | grep 'Data Space Available'")
        if Available.split()[4] == 'TB':
            try:
                value = float(Available.split()[3])*1000
            except Exception,err:
                logging.error("Get Value failed case TB:%s" %str(err))
                sys.exit(3)
	elif Available.split()[4] == 'GB':
	    try:
		value = float(Available.split()[3])
            except Exception,err:
                logging.error("Get Value failed case GB:%s" %str(err))
                sys.exit(4)
	else:
	    value = 1
    return value
def create_record():
    record = {}
    record['metric'] = 'docker.status'
    record['endpoint'] = ip.split('\n')[0]+'_'+os.uname()[1]
    record['timestamp'] = int(time.time())
    record['step'] = 300
    record['value'] = getvalue()
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
if data:
   print json.dumps(data)
