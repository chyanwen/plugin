#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2016.12.15
#Version：1.0
#V1.0 Description：nginx活跃连接数 usage:NginxrpActiveConn.py

import os
import time
import commands
import json
import sys
import re
import urllib2
import platform
import logging
import re
import ConfigParser
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
cf = ConfigParser.ConfigParser()
cf.read(r'args.conf')
if 'NginxrpActiveConn' not in cf.sections():
    logging.error('Config section wrong!')
    sys.exit(9)
if len(cf.items('NginxrpActiveConn'))!=1:
    logging.error("Need only one ip!")

ip=cf.items('NginxrpActiveConn')[0][1]
ts=int(time.time())
step=60
counter_list=[]
flag=0
out=commands.getoutput('curl http://%s/reverse-status' % ip)

for line in out.split('\n'):
    if re.search('Active connections',line):
        value=int(line.split(':')[1])
        flag=1
        counter_list.append({"endpoint":endpoint,"metric":"nginx.active_connections","tags":"","timestamp":ts,"step":step,"counterType":"GAUGE","value":value})    
    if re.search('Reading',line):
        counter_list.append({"endpoint":endpoint,"metric":"nginx.reading","tags":"","timestamp":ts,"step":step,"counterType":"GAUGE","value":int(line.split()[1])}) 
        counter_list.append({"endpoint":endpoint,"metric":"nginx.writing","tags":"","timestamp":ts,"step":step,"counterType":"GAUGE","value":int(line.split()[3])}) 
        counter_list.append({"endpoint":endpoint,"metric":"nginx.waiting","tags":"","timestamp":ts,"step":step,"counterType":"GAUGE","value":int(line.split()[5])}) 

if flag ==0:
   logging.error("Get nginx Active connections failed!")
   sys.exit(3)

print json.dumps(counter_list)
