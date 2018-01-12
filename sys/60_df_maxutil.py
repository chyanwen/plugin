#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.05.17
#Version：1.0
#V1.0 Description:监控分区磁盘使用率及inodes使用率，取使用率最高的值 

import os
import sys
import time
import json
import commands
import urllib2
import platform
import logging
import re

endpoint="default"
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

counter_list=[]
ts=int(time.time())
step=60
df_disk_list=commands.getoutput('df -h 2>/dev/null').split('\n')[1:]
df_inodes_list=commands.getoutput('df -i 2>/dev/null').split('\n')[1:]
df_disk_maxutil=0
df_inodes_maxutil=0
try:
    for item in df_disk_list :
        if '/etc/hosts' not in item.split()[5] and 'tmpfs' not in item.split()[0] and 'loop' not in item.split()[0] and 'shm' not in item.split()[0] and '/mnt' not in item.split()[5]:
            if int(item.split()[4].split('%')[0]) > df_disk_maxutil:
                df_disk_maxutil = int(item.split()[4].split('%')[0])

    for item in df_inodes_list:
            if '-' not in item.split()[4] and 'tmpfs' not in item.split()[0] and 'loop' not in item.split()[0] and '/etc/hosts' not in item.split()[5] and 'shm' not in item.split()[0] and '/mnt' not in item.split()[5]:
                if int(item.split()[4].split('%')[0]) > df_inodes_maxutil:
                    df_inodes_maxutil = int(item.split()[4].split('%')[0])

except Exception,err:
    logging.error("Get value failed, %s" %str(err))
    sys.exit(3)
counter_list.append({"endpoint":endpoint,"metric":"df.disk.maxutil","timestamp": ts, "step": step,"value": df_disk_maxutil, "counterType": "GAUGE", "tags":""})
counter_list.append({"endpoint":endpoint,'metric':"df.inodes.maxutil","timestamp": ts, "step": step,"value": df_inodes_maxutil, "counterType": "GAUGE", "tags":""})
print json.dumps(counter_list)
