#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.05.12
#Version：1.0
#V1.0 Description：监控 python log_keywords_monitor.py

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
#根据不同系统确认不同的获取内网ip方式
if 'centos' in platform.platform():
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192\.168|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192\.168|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging.error("UNKNOWN platform!")
    sys.exit(1)

#获取openfalcon格式的endpoint
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
#判断文件是否存在，没有则创建空文件
if not os.path.isfile(r'.apppay_log_record'):
    open(r'.apppay_log_record','w').close()
#获取位置记录
logfile='/var/log/vod/app-pay.log'
if not os.path.exists(logfile):
    logging.error("%s is not exists!" %logfile)
inode=os.stat(logfile).st_ino
position=0
with open(r'.apppay_log_record','r') as apppay_log_record_fd:
    tmp_list=apppay_log_record_fd.readlines()
if len(tmp_list)!=0:
    if inode==int(tmp_list[0]):
        position=int(tmp_list[1])

#初始化openfalcon push格式数据
ts=int(time.time())
step=300
counter_list=[]
#监控日志错误码及相应订单
with open(logfile,'r') as logfile_fd:
    logfile_fd.seek(position)
    for line in logfile_fd:
        if 'err_code' in line:
            errorcode=int(line.split()[2])
            order_id=line.split()[0].split(":")[1]
            if errorcode!=0:
                counter_list.append({"endpoint":endpoint,"metric":'third.callback.errcode',"tags":'third=tencent,order_id=%s' %order_id,"timestamp":ts,"step":step,"counterType":"GAUGE","value":errorcode})
    position=logfile_fd.tell()
#记录每个监控日志的结束位置及inode
with open('.apppay_log_record','w') as write_apppay_record_fd:
    write_apppay_record_fd.write("%d\n" %inode)
    write_apppay_record_fd.write("%d\n" %position)

    
print json.dumps(counter_list)










