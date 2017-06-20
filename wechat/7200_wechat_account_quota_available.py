#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.05.10
#Version：1.0
#V1.0 Description：监控account quota剩余数量 useage:wechat_account_quota_available.py 上限值

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

step=7200
counter_list=[]
ts=int(time.time())

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
if 'wechat_account_quota_available' not in cf.sections():
    logging.error('Config section wrong!')
    sys.exit(9)
if len(cf.items('wechat_account_quota_available'))!=1:
    logging.error("Need one int type!")
    sys.exit(9)
try:
    limit-count=int(cf.items('wechat_account_quota_available')[0][1])
except Exception,e:
    logging.error("Need one int type!")
    sys.exit(9)
try:
    result=commands.getoutput("mysql -uroot -phitv wechattv -e 'SELECT COUNT(*) FROM qrcode;' 2>/dev/null")
    count=int(result.split("\n")[1])
except Exception,e:
    logging.error("%s" %str(e))
    sys.exit(7)
counter_list.append({"endpoint": endpoint, "metric": "account.quota.available", "timestamp": ts, "step": step, "value": limit-count, "counterType": "GAUGE", "tags": ""})
print json.dumps(counter_list)
