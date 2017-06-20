#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import json
import os
import time
import commands
import platform
import sys
data=[]
if 'centos' in platform.platform():
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192\.168|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192\.168|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    print "UNKNOWN platform!\n"
    sys.exit(1)
def fetch_ntp_state():
    offset = 0
    try:
        raw_data = Popen(['ntpq', '-pn'], stdout=PIPE, stderr=PIPE).communicate()[0]
        for line in raw_data.splitlines():
            if line.startswith('*'):
                offset = line.split()[8]
    except OSError:
        pass

    create_record(offset)

def create_record(value):
    record = {}
    record['metric'] = 'sys.ntp.offset'
    record['endpoint'] = ip.split('\n')[0]+'_'+os.uname()[1]
    record['timestamp'] = int(time.time())
    record['step'] = 600
    record['value'] = abs(float(value))
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)

fetch_ntp_state()

if data:
    print json.dumps(data)
