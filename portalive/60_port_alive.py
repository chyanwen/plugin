#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.03.30
#Version：1.0
#V1.0 Description：监控端口的存活 使用：port_alive.py

import sys
import json
import time
import os
import re
import urllib2
import logging
import commands
import platform
import ConfigParser

logging.basicConfig(level=logging.ERROR,
                    filename='/home/work/open-falcon/agent/plugin/error.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

if 'centos' in platform.platform():
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192\.168|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192\.168|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging.error("UNKNOWN platform!")
    sys.exit(1)

if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',ip.split('\n')[0]):
    endpoint=ip.split('\n')[0]+'_'+os.uname()[1]
else:
    logging.error("Get internal ip failed, %s!" %ip.split('\n')[0])
    sys.exit(2)

#切换目录
try:
    os.chdir(r'/home/work/open-falcon/conf')
except Exception,e:
    logging.error(str(e))
    sys.exit(3)
#判断配置文件是否存在
if not os.path.exists(r'args.conf'):
    logging.error('args.conf is not exists!')
    sys.exit(4)
#获取参数值
port_list=[]
cf = ConfigParser.ConfigParser()
cf.read(r'args.conf')
if 'port_alive' not in cf.sections():
    logging.error('Config section wrong!')
    sys.exit(9)
for item in cf.items('port_alive'):
    port_list.append(item[1])

ts=int(time.time())
step=60
port_listen_list=[]
counter_list=[]
result=commands.getoutput("/usr/sbin/ss -nlt 2>/dev/null").split('\n')[1:]
if result == []:
    logging.error("run command '/usr/sbin/ss -nlt 2>/dev/null' failed!")
    sys.exit(5)
for line in result:
    port_listen_list.append(line.split()[3].split(':')[-1])

for port in port_list:
    if port in port_listen_list:
        counter_list.append({"endpoint":endpoint,"metric":"port.alive","tags":"port=%s" %port,"timestamp":ts,"step":step,"counterType":"GAUGE","value":1})
    else:
        counter_list.append({"endpoint":endpoint,"metric":"port.alive","tags":"port=%s" %port,"timestamp":ts,"step":step,"counterType":"GAUGE","value":0})

print json.dumps(counter_list)
