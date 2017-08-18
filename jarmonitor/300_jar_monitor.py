#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.03.31
#Version：1.0
#V1.0 Description：监控java网元状态

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
    sys.exit(3)
#获取参数值
jar_list=[]
cf = ConfigParser.ConfigParser()
cf.read(r'args.conf')
if 'jar_monitor' not in cf.sections():
    logging.error('Config section wrong!')
    sys.exit(9)
for item in cf.items('jar_monitor'):
    jar_list.append(item[1])

ts=int(time.time())
step=300
counter_list=[]
for jar in jar_list:
    try:
        jar_info=commands.getoutput("ps -ef 2>/dev/null| grep '%s.jar' | grep -v 'grep'" %jar)
        if jar_info:
            processID=jar_info.split()[1]
            java_jstack=jar_info.split()[7].replace("bin/java","bin/jstack")
            block_num=int(commands.getoutput("%s -l %s 2>/dev/null| egrep 'blocked|dead lock' |wc -l" %(java_jstack,processID)))
            if block_num:
                counter_list.append({"endpoint":endpoint,"metric":"jar.status","tags":"jar=%s" %jar,"timestamp":ts,"step":step,"counterType":"GAUGE","value":0})
            else:
                counter_list.append({"endpoint":endpoint,"metric":"jar.status","tags":"jar=%s"  %jar,"timestamp":ts,"step":step,"counterType":"GAUGE","value":1})
        else:
            counter_list.append({"endpoint":endpoint,"metric":"jar.status","tags":"jar=%s" %jar,"timestamp":ts,"step":step,"counterType":"GAUGE","value":0})
    except Exception,err:
        logging("get value failed! %s" %str(err))
        sys.exit(4)
print json.dumps(counter_list)
