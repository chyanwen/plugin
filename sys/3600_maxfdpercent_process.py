#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.06.08
#Version：1.0
#V1.0 Description:监控进程占用句柄数的比例，取最大值

import os
import time
import re
import json
import commands
import platform
import sys
import logging 
counter_list=[]
process_fd_percent=[]
step=3600
ts=int(time.time())
endpoint="default"
logging.basicConfig(level=logging.INFO,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

try:
    pid_list=commands.getoutput("ps -ef | awk '{print $2}'").split('\n')[1:]
except Exception,err:
    logging.error("Run command failed:%s" %str(err))
    sys.exit(3)

for pid in pid_list:
    try:
        proc_fd_maxnum=commands.getoutput("cat /proc/%s/limits | awk '/^Max open files/{print $5}'" %pid)
        fd_num=len(os.listdir('/proc/%s/fd' %pid))
	percent=float(fd_num)/float(proc_fd_maxnum)*100
        process_fd_percent.append(percent)
    except Exception,e:
        logging.error(str(e))
        process_fd_percent.append(float(0))
try:
    sys_fds_used=commands.getoutput("cat /proc/sys/fs/file-nr | awk '{print $1}'")
    sys_fds_total=commands.getoutput("cat /proc/sys/fs/file-nr | awk '{print $3}'")
    sys_fds_percent=float(sys_fds_used)/float(sys_fds_total)*100
except Exception,e:
    logging.error(str(e))
    sys.exit(7)
counter_list.append({ "endpoint": endpoint, "metric": "procs.fds.maxpercent", "timestamp": ts, "step": step, "value": max(process_fd_percent), "counterType": "GAUGE", "tags": "",})
counter_list.append({ "endpoint": endpoint, "metric": "sys.fds.used", "timestamp": ts, "step": step, "value": int(sys_fds_used), "counterType": "GAUGE", "tags": "",})
counter_list.append({ "endpoint": endpoint, "metric": "sys.fds.percent", "timestamp": ts, "step": step, "value": sys_fds_percent, "counterType": "GAUGE", "tags": "",})

print json.dumps(counter_list)
