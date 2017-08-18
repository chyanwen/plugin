#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.03.30
#Version：1.0
#V1.0 Description：监控端口的存活 使用：port_alive.py port1 port2 ...

import sys
import json
import time
import os
import re
import urllib2
import logging
import commands
import platform

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

ts=int(time.time())
step=3600
counter_list=[]
try:
    result=commands.getoutput("ls -l /usr/sse/home/vod_media/data/tlog 2>/dev/null | wc -l")
except Exception,e:
    logging.error(str(e))
    sys.exit(3)
counter_list.append({"endpoint":endpoint,"metric":"sse.tlog.files","tags":"" ,"timestamp":ts,"step":step,"counterType":"GAUGE","value":int(result)})
print json.dumps(counter_list)
