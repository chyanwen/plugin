#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.06.13
#Version：1.0
#V1.0 Description:check agent and plugin version

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

ts=int(time.time())
step=1800
counter_list=[]
sum=0
try:
    agent_version=commands.getoutput("cat /home/work/open-falcon/agent/gitversion")
    plugin_version=commands.getoutput("cat /home/work/open-falcon/agent/plugin/version")
    agent_version=float(agent_version)
    plugin_version=float(plugin_version)
except Exception,e:
    agent_version=0.0
    plugin_version=0.0
    pass

counter_list.append({ "endpoint": endpoint, "metric": "agent.version" , "timestamp": ts, "step": step, "value": agent_version, "counterType": "GAUGE", "tags": "name=agent",})
counter_list.append({ "endpoint": endpoint, "metric": "plugin.version" , "timestamp": ts, "step": step, "value": plugin_version, "counterType": "GAUGE", "tags": "name=plugin",})


#print counter_list

request = urllib2.Request("http://127.0.0.1:1988/v1/push", data=json.dumps(counter_list))
try:
    response = urllib2.urlopen(request,timeout=5)
    print response.read()
except Exception,e:
    logging.error("Push data failed, %s" %str(e))
    sys.exit(4)
