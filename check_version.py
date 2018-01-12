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
endpoint="default"
logging.basicConfig(level=logging.ERROR,  
                    filename='/home/work/open-falcon/agent/plugin/error.log',  
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

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
