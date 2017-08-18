#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.05.11
#Version：1.0
#V1.0 Description：监控日志字段 使用：修改配置文件logmonitor.conf；执行 python log_keywords_monitor.py

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
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
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
#判断日志记录文件是否存在，没有则创建空文件
if not os.path.isfile(r'.log_record'):
    open(r'.log_record','w').close()
#判断配置文件是否存在
if not os.path.exists(r'logmonitor.conf'):
    logging.error('logmonitor.conf is not exists!')
    sys.exit(4)
#读取配置文件
cf=ConfigParser.ConfigParser()
cf.read(r'logmonitor.conf')
sections=cf.sections()
logfiles=[]
inodes=[]
positions=[]
for section in sections:
    logfiles.append(cf.items(section)[0][1]+cf.items(section)[1][1])
with open(r'.log_record','r') as log_record_fd:
    log_record_fd_index=1
    for log_record_fd_line in log_record_fd:
        if log_record_fd_index%2==1:
            inodes.append(log_record_fd_line)
        else:
            positions.append(log_record_fd_line)
        log_record_fd_index+=1
#判断要监控的日志是否存在
for logfile in logfiles:
    if not os.path.exists(logfile):
        logging.error("%s is not exists!" %logfile)
        sys.exit(4)
#如果记录监控日志位置的文件为空，inodes置为空列表
if len(positions)==0:
    inodes=[]
#如果记录监控日志位置的文件位置点个数多于logfiles文件个数，截断inodes及positions列表值
if len(positions)>len(logfiles):
    cut_num=len(positions)-len(logfiles)
    for cut_values in range(cut_num):
        inodes.pop()
        positions.pop()
#在遍历监控的日志文件之前确认日志是否切割及上一次日志的标记位置
for index in range(len(logfiles)):
    if index<len(positions):
        if os.stat(logfiles[index]).st_ino!=int(inodes[index]):
            inodes[index]=os.stat(logfiles[index]).st_ino
            positions[index]=0
        else:
            inodes[index]=int(inodes[index])
            positions[index]=int(positions[index])
    else:
        inodes.append(os.stat(logfiles[index]).st_ino)
        positions.append(0)
#初始化openfalcon push格式数据
ts=int(time.time())
step=300
counter_list=[]
#遍历所有的日志文件进行指定字段监控
for monitor_index in range(len(logfiles)):
    keswords_list=[]
    metric_list=[]
    tags_list=[]
    try:
        keywords_list=eval(cf.items(sections[monitor_index])[2][1])
        metric_list=eval(cf.items(sections[monitor_index])[3][1])
        tags_list=eval(cf.items(sections[monitor_index])[4][1])
    except Exception,e:
        logging.error("function eval error:%s" %str(e))
        sys.exit(5)
    values_list=[0 for i in range(len(keywords_list))]
    with open(logfiles[monitor_index],'r') as logfile_fd:
        logfile_fd.seek(positions[monitor_index])
        for line in logfile_fd:
            for index in range(len(keywords_list)):
                if re.search(keywords_list[index],line):
                    values_list[index]+=1
        positions[monitor_index]=logfile_fd.tell()  
    for index in range(len(keywords_list)):
        counter_list.append({"endpoint":endpoint,"metric":metric_list[index],"tags":tags_list[index],"timestamp":ts,"step":step,"counterType":"GAUGE","value":values_list[index]})

#记录每个监控日志的结束位置及inode
with open('.log_record','w') as write_record_fd:
    for index in range(len(inodes)):
        write_record_fd.write("%d\n" %inodes[index])
        write_record_fd.write("%d\n" %positions[index])

    
print json.dumps(counter_list)
#request = urllib2.Request("http://127.0.0.1:1988/v1/push", data=json.dumps(counter_list))
#try:
#    response = urllib2.urlopen(request,timeout=5)
#    print response.read()
#except Exception,e:
#    logging.error("Push data failed, %s" %str(e))
#    sys.exit(6)










