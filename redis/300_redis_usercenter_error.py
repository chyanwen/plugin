#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.03.28
#Version：1.0
#V1.0 Description：monitor sync usercenter 

import sys 
import json
import time
import os
import re
import urllib2
import commands
import platform
import logging
from subprocess import Popen,PIPE

logging.basicConfig(level=logging.ERROR,
                    filename='/home/work/open-falcon/agent/plugin/error.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]

ts=int(time.time())
step=300
counter_list=[]
if 'wsvodr-b' in endpoint: 
    len_usercenter_error=int(commands.getoutput("redis-cli -p 6381 llen order_need_notify_member"))
    len_user_coupon_error=int(commands.getoutput("redis-cli -p 6381 llen user_coupon"))
    counter_list.append({"endpoint":endpoint,"metric":"redis.order.notify.member","timestamp": ts, "step": step, "value": len_usercenter_error, "counterType": "GAUGE", "tags": "",})
    counter_list.append({"endpoint":endpoint,"metric":"redis.order.coupon","timestamp": ts, "step": step, "value": len_user_coupon_error, "counterType": "GAUGE", "tags": "",})
    print json.dumps(counter_list)
elif 'txvod-d' in endpoint:
    len_usercenter_error=int(commands.getoutput("redis-cli -p 6379 llen order_need_notify_member"))
    len_user_coupon_error=int(commands.getoutput("redis-cli -p 6379 llen user_coupon"))
    counter_list.append({"endpoint":endpoint,"metric":"redis.order.notify.member","timestamp": ts, "step": step, "value": len_usercenter_error, "counterType": "GAUGE", "tags": "",})
    counter_list.append({"endpoint":endpoint,"metric":"redis.order.coupon","timestamp": ts, "step": step, "value": len_user_coupon_error, "counterType": "GAUGE", "tags": "",})
    print json.dumps(counter_list)
elif 'ykvod-d' in endpoint:
    len_usercenter_error=int(commands.getoutput("redis-cli -p 6379 llen order_need_notify_member"))
    len_user_coupon_error=int(commands.getoutput("redis-cli -p 6379 llen user_coupon"))
    counter_list.append({"endpoint":endpoint,"metric":"redis.order.notify.member","timestamp": ts, "step": step, "value": len_usercenter_error, "counterType": "GAUGE", "tags": "",})
    counter_list.append({"endpoint":endpoint,"metric":"redis.order.coupon","timestamp": ts, "step": step, "value": len_user_coupon_error, "counterType": "GAUGE", "tags": "",})
    print json.dumps(counter_list)
else:
    print json.dumps([])
