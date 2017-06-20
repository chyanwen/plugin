#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.06.08
#Version：1.0
#V1.0 Description:监控进程占用句柄数的比例，取最大值

import os
import time
import json
import commands
import platform
import sys
import logging 
data=[]
process_fd_percent=[]
logging.basicConfig(level=logging.INFO,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
if 'centos' in platform.platform():
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192\.168|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192\.168|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging.error("UNKNOWN platform!\n")
    sys.exit(1)


try:
    sys_max_openfiles=int(commands.getoutput("ulimit -a 2>/dev/null | awk '/^open files/{print $4}'"))
    pid_list=commands.getoutput("ps -ef | awk '{print $2}'").split('\n')[1:]
except Exception,err:
    logging.error("Run command failed:%s" %str(err))
    sys.exit(2)

for pid in pid_list:
    try:
        fd_num=int(commands.getoutput("lsof -n -p %s 2>/dev/null |wc -l" %pid))
        percent=float(fd_num)/float(sys_max_openfiles)*100
	if percent>=50.0:
            proc_fd_maxnum=commands.getoutput("cat /proc/%s/limits | awk '/^Max open files/{print $5}'" %pid)
            percent=float(fd_num)/float(proc_fd_maxnum)
        process_fd_percent.append(percent)
    except Exception,e:
        logging.error(str(e))
        sys.exit(7)
def create_record():
    record = {}
    record['metric'] = 'procs.fds.maxpercent'
    record['endpoint'] = ip.split('\n')[0]+'_'+os.uname()[1]
    record['timestamp'] = int(time.time())
    record['step'] = 1800
    record['value'] = max(process_fd_percent)
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)
create_record()
if data:
   print json.dumps(data)
