#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2
import time
from urllib import urlencode
import json
import os
import sys
import time
import urllib2
import platform
import logging
import re
import commands


endpoint="default"
logging.basicConfig(level=logging.ERROR,
                    filename='/home/work/open-falcon/agent/plugin/error.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')



with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

#es_health_code: 0,1 0 represent problem; 1 represent healthy
counter_list=[]
ts=int(time.time())
step=60

try:

    res = urllib2.urlopen('http://192.168.11.184:9200/_cluster/health',timeout=5)
    
    res_dict = json.loads(res.read())

    status = res_dict.get('status')
    number_of_nodes = res_dict.get('number_of_nodes')
    number_of_data_nodes = res_dict.get('number_of_data_nodes')
    relocating_shards = res_dict.get('relocating_shards')
    initializing_shards = res_dict.get('initializing_shards')
    unassigned_shards = res_dict.get('unassigned_shards')
    delayed_unassigned_shards = res_dict.get('delayed_unassigned_shards')   

    es_health_geturl=1

    if status == "green" or status == "yellow":
        status=1
    else:
       status=0

    counter_list.append({'endpoint': endpoint,'metric': 'es.health.geturl',"timestamp": ts, "step": step,"value": es_health_geturl, "counterType": "GAUGE", "tags": ""})
 
    counter_list.append({'endpoint':endpoint,'metric':'es.health.status',"timestamp": ts, "step": step,"value": status, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.number_of_nodes',"timestamp": ts, "step": step,"value": number_of_nodes, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.number_of_data_nodes',"timestamp": ts, "step": step,"value": number_of_data_nodes, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.relocating_shards',"timestamp": ts, "step": step,"value": relocating_shards, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.initializing_shards',"timestamp": ts, "step": step,"value": initializing_shards, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.unassigned_shards',"timestamp": ts, "step": step,"value": unassigned_shards, "counterType": "GAUGE", "tags":""})
    counter_list.append({'endpoint':endpoint,'metric':'es.health.delayed_unassigned_shards',"timestamp": ts, "step": step,"value": delayed_unassigned_shards, "counterType": "GAUGE", "tags":""})    



except:
    es_health_geturl=0
    counter_list.append({'endpoint':endpoint,'metric':'es.health.geturl',"timestamp": ts, "step": step,"value": es_health_geturl, "counterType": "GAUGE", "tags":""})



print json.dumps(counter_list)







