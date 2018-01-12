#!/usr/bin/env python

import os
import sys
import time
import json
import commands
import urllib2


counter_list=[]
ts=int(time.time())
step=60

endpoint="default"

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

cmd='''curl -u admin:admin http://%s:8161/admin/queues.jsp 2>/dev/null |grep JMSDestination=Consumer | awk -F "?" '{print $2}' |sed "s/\\">.*//g" | sed "s/&.*//g"|sort -u | sed "s/JMSDestination=//g"''' %ip_list.split('\n')[0]

mq_queue=commands.getoutput(cmd)
mq_queue=mq_queue.split('\n')

for i in mq_queue:
	cmd='''curl -u admin:admin http://%s:8161/admin/queues.jsp 2>/dev/null |grep -m 2 -A 2 %s | egrep -m 1 "<td>[0-9]+" | awk -F "<|>" '{print $3}' ''' %(ip_list.split('\n')[0],i)
	pending_queue_num=commands.getoutput(cmd)
	counter_list.append({'endpoint':endpoint,'metric':i,"timestamp": ts, "step": step,"value": pending_queue_num, "counterType": "GAUGE", "tags":""})

print json.dumps(counter_list)
