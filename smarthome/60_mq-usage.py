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


ip_list=commands.getoutput("ifconfig|egrep 'inet 192\.168|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")

endpoint=ip_list.split('\n')[0]+'_'+os.uname()[1]

cmd= '''curl http://%s:8161/admin/index.jsp 2>/dev/null |grep -A 1 "Store percent used" | sed "1d" | sed 's/<..>//g'|sed 's/<...>//g'|sed 's/<.>//g' |sed "s/ //g"''' %ip_list.split('\n')[0]
store_usage=commands.getoutput(cmd)

cmd='''curl http://%s:8161/admin/index.jsp 2>/dev/null |grep -A 1 "Memory percent used" | sed "1d" | sed 's/<..>//g'|sed 's/<...>//g'|sed 's/<.>//g' |sed "s/ //g"''' %ip_list.split('\n')[0]
mem_usage=commands.getoutput(cmd)

cmd='''curl http://%s:8161/admin/index.jsp 2>/dev/null |grep -A 1 "Temp percent used" | sed "1d" | sed 's/<..>//g'|sed 's/<...>//g'|sed 's/<.>//g' |sed "s/ //g"''' %ip_list.split('\n')[0]
temp_usage=commands.getoutput(cmd)


counter_list.append({'endpoint':endpoint,'metric':'mq.store.usage',"timestamp": ts, "step": step,"value": store_usage, "counterType": "GAUGE", "tags":""})
counter_list.append({'endpoint':endpoint,'metric':'mq.mem.usage',"timestamp": ts, "step": step,"value": mem_usage, "counterType": "GAUGE", "tags":""})
counter_list.append({'endpoint':endpoint,'metric':'mq.temp.usage',"timestamp": ts, "step": step,"value": temp_usage, "counterType": "GAUGE", "tags":""})

print json.dumps(counter_list)
