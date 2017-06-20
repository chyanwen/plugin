#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen & tanhao
#Date：2017.05.18
#Version：3.0
#V1.0 Description：监控收入订单数

import sys
import json
import time
import os
import re
import urllib2
import logging
import commands
import platform
import MySQLdb

logging.basicConfig(level=logging.ERROR,
                    filename='/home/work/open-falcon/agent/plugin/error.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

if 'centos' in platform.platform():
    ip=commands.getoutput("/usr/sbin/ifconfig|egrep 'inet 192\.168|inet 10|inet 172\.1[6-9]|inet 172\.2[0-9]|inet 172\.3[01]'| awk '{print $2}'")
elif 'SuSE' in platform.platform():
    ip=commands.getoutput("/sbin/ifconfig|egrep 'inet addr:192\.168|inet addr:10|inet addr:172\.1[6-9]|inet addr:172\.2[0-9]|inet addr:172\.3[01]'| awk -F':' '{print $2}'| awk '{print $1}'")
else:
    logging.error("UNKNOWN platform!")
    sys.exit(1)

if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',ip.split('\n')[0]):
    endpoint=ip.split('\n')[0]+'_'+os.uname()[1]
else:
    logging.error("Get internal ip failed, %s!" %ip.split('\n')[0])
    sys.exit(2)
def gettime():
    time_now=time.time()
    time_halfhour_ago=time_now-1800
    time_day=time.localtime(time_now)
    time_day=list(time_day)
    time_day[3]=0
    time_day[4]=0
    time_day[5]=0
    time_day=tuple(time_day)
    time_day=time.mktime(time_day)
    return int(time_day),int(time_now),int(time_halfhour_ago)
    
time_day,ts,time_halfhour_ago=gettime()
step=1800
try:
    conn=MySQLdb.connect(ip.split('\n')[0],'root','mysql')
    cur=conn.cursor()
    counter_list=[]
    if 'edu' in endpoint:
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=1 and m.status in (3,7)' %time_day)
        edu_zhifubao_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=1 and m.status=0' %time_day)
        edu_zhifubao_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=1' %time_day)
        edu_zhifubao_total=int(cur.fetchone()[0])
        edu_zhifubao_fail=edu_zhifubao_total - edu_zhifubao_success - edu_zhifubao_notpay
        if edu_zhifubao_total==0:
            edu_zhifubao_successrate=100.0
        else:
            edu_zhifubao_successrate=100*float(edu_zhifubao_success) / float(edu_zhifubao_total)
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=2 and m.status in (3,7)' %time_day)
        edu_weixin_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=2 and m.status=0' %time_day)
        edu_weixin_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=2' %time_day)
        edu_weixin_total=int(cur.fetchone()[0])
        edu_weixin_fail=edu_weixin_total - edu_weixin_success - edu_weixin_notpay
        if edu_weixin_total==0:
            edu_weixin_successrate=100.0
        else:
            edu_weixin_successrate=100*float(edu_weixin_success) / float(edu_weixin_total)
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=1 and m.status in (3,7)' %time_halfhour_ago)
        edu_zhifubao_last30mins_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=1 and m.status=0' %time_halfhour_ago)
        edu_zhifubao_last30mins_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=1' %time_halfhour_ago)
        edu_zhifubao_last30mins_total=int(cur.fetchone()[0])
        edu_zhifubao_last30mins_fail=edu_zhifubao_last30mins_total - edu_zhifubao_last30mins_success - edu_zhifubao_last30mins_notpay
        if edu_zhifubao_last30mins_total==0:
            edu_zhifubao_last30mins_successrate=100.0
        else:
            edu_zhifubao_last30mins_successrate=100*float(edu_zhifubao_last30mins_success) / float(edu_zhifubao_last30mins_total)
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=2 and m.status in (3,7)' %time_halfhour_ago)
        edu_weixin_last30mins_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=2 and m.status=0' %time_halfhour_ago)
        edu_weixin_last30mins_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from edu.order_info m where m.created_time>%d and m.pay_platform=2' %time_halfhour_ago)
        edu_weixin_last30mins_total=int(cur.fetchone()[0])
        edu_weixin_last30mins_fail=edu_weixin_last30mins_total - edu_weixin_last30mins_success - edu_weixin_last30mins_notpay
        if edu_weixin_last30mins_total==0:
            edu_weixin_last30mins_successrate=100.0
        else:
            edu_weixin_last30mins_successrate=100*float(edu_weixin_last30mins_success) / float(edu_weixin_last30mins_total)
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_success, "counterType": "GAUGE", "tags": "platform=zfb,status=success,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_notpay, "counterType": "GAUGE", "tags": "platform=zfb,status=notpay,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_total, "counterType": "GAUGE", "tags": "platform=zfb,status=all,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_fail, "counterType": "GAUGE", "tags": "platform=zfb,status=fail,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_successrate, "counterType": "GAUGE", "tags": "platform=zfb,status=successrate,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_success, "counterType": "GAUGE", "tags": "platform=wx,status=success,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_notpay, "counterType": "GAUGE", "tags": "platform=wx,status=notpay,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_total, "counterType": "GAUGE", "tags": "platform=wx,status=all,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_fail, "counterType": "GAUGE", "tags": "platform=wx,status=fail,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_successrate, "counterType": "GAUGE", "tags": "platform=wx,status=successrate,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_last30mins_success, "counterType": "GAUGE", "tags": "platform=zfb,status=success,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_last30mins_notpay, "counterType": "GAUGE", "tags": "platform=zfb,status=notpay,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_last30mins_total, "counterType": "GAUGE", "tags": "platform=zfb,status=all,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_last30mins_fail, "counterType": "GAUGE", "tags": "platform=zfb,status=fail,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_zhifubao_last30mins_successrate, "counterType": "GAUGE", "tags": "platform=zfb,status=successrate,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_last30mins_success, "counterType": "GAUGE", "tags": "platform=wx,status=success,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_last30mins_notpay, "counterType": "GAUGE", "tags": "platform=wx,status=notpay,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_last30mins_total, "counterType": "GAUGE", "tags": "platform=wx,status=all,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_last30mins_fail, "counterType": "GAUGE", "tags": "platform=wx,status=fail,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "edu.order", "timestamp": ts, "step": step, "value": edu_weixin_last30mins_successrate, "counterType": "GAUGE", "tags": "platform=wx,status=successrate,interval=last30mins"})
    elif 'wsvod' in endpoint:
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status in (5,7)' %time_day)
        wsvod_zhifubao_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status=0' %time_day)
        wsvod_zhifubao_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1' %time_day)
        wsvod_zhifubao_total=int(cur.fetchone()[0])
        wsvod_zhifubao_fail=wsvod_zhifubao_total - wsvod_zhifubao_success - wsvod_zhifubao_notpay
        if wsvod_zhifubao_total==0:
            wsvod_zhifubao_successrate=100.0
        else:
            wsvod_zhifubao_successrate=100*float(wsvod_zhifubao_success) / float(wsvod_zhifubao_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status in (5,7)' %time_day)
        wsvod_weixin_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status=0' %time_day)
        wsvod_weixin_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2' %time_day)
        wsvod_weixin_total=int(cur.fetchone()[0])
        wsvod_weixin_fail=wsvod_weixin_total - wsvod_weixin_success - wsvod_weixin_notpay
        if wsvod_weixin_total==0:
            wsvod_weixin_successrate=100.0
        else:
            wsvod_weixin_successrate=100*float(wsvod_weixin_success) / float(wsvod_weixin_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1015 and m.status in (5,7)' %time_day)
        wsvod_wasu_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1015 and m.status=0' %time_day)
        wsvod_wasu_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1015' %time_day)
        wsvod_wasu_total=int(cur.fetchone()[0])
        wsvod_wasu_fail=wsvod_wasu_total - wsvod_wasu_success - wsvod_wasu_notpay
        if wsvod_wasu_total==0:
            wsvod_wasu_successrate=100.0
        else:
            wsvod_wasu_successrate=100*float(wsvod_wasu_success) / float(wsvod_wasu_total) 
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status in (5,7)' %time_halfhour_ago)
        wsvod_zhifubao_last30mins_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status=0' %time_halfhour_ago)
        wsvod_zhifubao_last30mins_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1' %time_halfhour_ago)
        wsvod_zhifubao_last30mins_total=int(cur.fetchone()[0])
        wsvod_zhifubao_last30mins_fail=wsvod_zhifubao_last30mins_total - wsvod_zhifubao_last30mins_success - wsvod_zhifubao_last30mins_notpay
        if wsvod_zhifubao_last30mins_total==0:
            wsvod_zhifubao_last30mins_successrate=100.0
        else:
            wsvod_zhifubao_last30mins_successrate=100*float(wsvod_zhifubao_last30mins_success) / float(wsvod_zhifubao_last30mins_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status in (5,7)' %time_halfhour_ago)
        wsvod_weixin_last30mins_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status=0' %time_halfhour_ago)
        wsvod_weixin_last30mins_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2' %time_halfhour_ago)
        wsvod_weixin_last30mins_total=int(cur.fetchone()[0])
        wsvod_weixin_last30mins_fail=wsvod_weixin_last30mins_total - wsvod_weixin_last30mins_success - wsvod_weixin_last30mins_notpay
        if wsvod_weixin_last30mins_total==0:
            wsvod_weixin_last30mins_successrate=100.0
        else:
            wsvod_weixin_last30mins_successrate=100*float(wsvod_weixin_last30mins_success) / float(wsvod_weixin_last30mins_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1015 and m.status in (5,7)' %time_halfhour_ago)
        wsvod_wasu_last30mins_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1015 and m.status=0' %time_halfhour_ago)
        wsvod_wasu_last30mins_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1015' %time_halfhour_ago)
        wsvod_wasu_last30mins_total=int(cur.fetchone()[0])
        wsvod_wasu_last30mins_fail=wsvod_wasu_last30mins_total - wsvod_wasu_last30mins_success - wsvod_wasu_last30mins_notpay
        if wsvod_wasu_last30mins_total==0:
            wsvod_wasu_last30mins_successrate=100.0
        else:
            wsvod_wasu_last30mins_successrate=100*float(wsvod_wasu_last30mins_success) / float(wsvod_wasu_last30mins_total)
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_success, "counterType": "GAUGE", "tags": "platform=zfb,status=success,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_notpay, "counterType": "GAUGE", "tags": "platform=zfb,status=notpay,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_total, "counterType": "GAUGE", "tags": "platform=zfb,status=all,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_fail, "counterType": "GAUGE", "tags": "platform=zfb,status=fail,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_successrate, "counterType": "GAUGE", "tags": "platform=zfb,status=successrate,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_success, "counterType": "GAUGE", "tags": "platform=wx,status=success,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_notpay, "counterType": "GAUGE", "tags": "platform=wx,status=notpay,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_total, "counterType": "GAUGE", "tags": "platform=wx,status=all,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_fail, "counterType": "GAUGE", "tags": "platform=wx,status=fail,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_successrate, "counterType": "GAUGE", "tags": "platform=wx,status=successrate,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_success, "counterType": "GAUGE", "tags": "platform=wasu,status=success,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_notpay, "counterType": "GAUGE", "tags": "platform=wasu,status=notpay,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_total, "counterType": "GAUGE", "tags": "platform=wasu,status=all,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_fail, "counterType": "GAUGE", "tags": "platform=wasu,status=fail,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_successrate, "counterType": "GAUGE", "tags": "platform=wasu,status=successrate,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_last30mins_success, "counterType": "GAUGE", "tags": "platform=zfb,status=success,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_last30mins_notpay, "counterType": "GAUGE", "tags": "platform=zfb,status=notpay,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_last30mins_total, "counterType": "GAUGE", "tags": "platform=zfb,status=all,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_last30mins_fail, "counterType": "GAUGE", "tags": "platform=zfb,status=fail,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_zhifubao_last30mins_successrate, "counterType": "GAUGE", "tags": "platform=zfb,status=successrate,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_last30mins_success, "counterType": "GAUGE", "tags": "platform=wx,status=success,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_last30mins_notpay, "counterType": "GAUGE", "tags": "platform=wx,status=notpay,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_last30mins_total, "counterType": "GAUGE", "tags": "platform=wx,status=all,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_last30mins_fail, "counterType": "GAUGE", "tags": "platform=wx,status=fail,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_weixin_last30mins_successrate, "counterType": "GAUGE", "tags": "platform=wx,status=successrate,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_last30mins_success, "counterType": "GAUGE", "tags": "platform=wasu,status=success,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_last30mins_notpay, "counterType": "GAUGE", "tags": "platform=wasu,status=notpay,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_last30mins_total, "counterType": "GAUGE", "tags": "platform=wasu,status=all,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_last30mins_fail, "counterType": "GAUGE", "tags": "platform=wasu,status=fail,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "wsvod.order", "timestamp": ts, "step": step, "value": wsvod_wasu_last30mins_successrate, "counterType": "GAUGE", "tags": "platform=wasu,status=successrate,interval=last30mins"})
    elif 'txvod' in endpoint:
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status in (5,7)' %time_day)
        txvod_zhifubao_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status=0' %time_day)
        txvod_zhifubao_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1' %time_day)
        txvod_zhifubao_total=int(cur.fetchone()[0])
        txvod_zhifubao_fail=txvod_zhifubao_total - txvod_zhifubao_success - txvod_zhifubao_notpay
        if txvod_zhifubao_total==0:
            txvod_zhifubao_successrate=100.0
        else:
            txvod_zhifubao_successrate=100*float(txvod_zhifubao_success) / float(txvod_zhifubao_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status in (5,7)' %time_day)
        txvod_weixin_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status=0' %time_day)
        txvod_weixin_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2' %time_day)
        txvod_weixin_total=int(cur.fetchone()[0])
        txvod_weixin_fail=txvod_weixin_total - txvod_weixin_success - txvod_weixin_notpay
        if txvod_weixin_total==0:
            txvod_weixin_successrate=100.0
        else:
            txvod_weixin_successrate=100*float(txvod_weixin_success) / float(txvod_weixin_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status in (5,7)' %time_halfhour_ago)
        txvod_zhifubao_last30mins_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status=0' %time_halfhour_ago)
        txvod_zhifubao_last30mins_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1' %time_halfhour_ago)
        txvod_zhifubao_last30mins_total=int(cur.fetchone()[0])
        txvod_zhifubao_last30mins_fail=txvod_zhifubao_last30mins_total - txvod_zhifubao_last30mins_success - txvod_zhifubao_last30mins_notpay
        if txvod_zhifubao_last30mins_total==0:
            txvod_zhifubao_last30mins_successrate=100.0
        else:
            txvod_zhifubao_last30mins_successrate=100*float(txvod_zhifubao_last30mins_success) / float(txvod_zhifubao_last30mins_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status in (5,7)' %time_halfhour_ago)
        txvod_weixin_last30mins_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status=0' %time_halfhour_ago)
        txvod_weixin_last30mins_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2' %time_halfhour_ago)
        txvod_weixin_last30mins_total=int(cur.fetchone()[0])
        txvod_weixin_last30mins_fail=txvod_weixin_last30mins_total - txvod_weixin_last30mins_success - txvod_weixin_last30mins_notpay
        if txvod_weixin_last30mins_total==0:
            txvod_weixin_last30mins_successrate=100.0
        else:
            txvod_weixin_last30mins_successrate=100*float(txvod_weixin_last30mins_success) / float(txvod_weixin_last30mins_total)
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_success, "counterType": "GAUGE", "tags": "platform=zfb,status=success,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_notpay, "counterType": "GAUGE", "tags": "platform=zfb,status=notpay,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_total, "counterType": "GAUGE", "tags": "platform=zfb,status=all,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_fail, "counterType": "GAUGE", "tags": "platform=zfb,status=fail,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_successrate, "counterType": "GAUGE", "tags": "platform=zfb,status=successrate,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_success, "counterType": "GAUGE", "tags": "platform=wx,status=success,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_notpay, "counterType": "GAUGE", "tags": "platform=wx,status=notpay,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_total, "counterType": "GAUGE", "tags": "platform=wx,status=all,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_fail, "counterType": "GAUGE", "tags": "platform=wx,status=fail,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_successrate, "counterType": "GAUGE", "tags": "platform=wx,status=successrate,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_last30mins_success, "counterType": "GAUGE", "tags": "platform=zfb,status=success,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_last30mins_notpay, "counterType": "GAUGE", "tags": "platform=zfb,status=notpay,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_last30mins_total, "counterType": "GAUGE", "tags": "platform=zfb,status=all,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_last30mins_fail, "counterType": "GAUGE", "tags": "platform=zfb,status=fail,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_zhifubao_last30mins_successrate, "counterType": "GAUGE", "tags": "platform=zfb,status=successrate,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_last30mins_success, "counterType": "GAUGE", "tags": "platform=wx,status=success,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_last30mins_notpay, "counterType": "GAUGE", "tags": "platform=wx,status=notpay,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_last30mins_total, "counterType": "GAUGE", "tags": "platform=wx,status=all,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_last30mins_fail, "counterType": "GAUGE", "tags": "platform=wx,status=fail,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "txvod.order", "timestamp": ts, "step": step, "value": txvod_weixin_last30mins_successrate, "counterType": "GAUGE", "tags": "platform=wx,status=successrate,interval=last30mins"})
    elif 'ykvod' in endpoint:
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status in (5,7)' %time_day)
        ykvod_zhifubao_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status=0' %time_day)
        ykvod_zhifubao_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1' %time_day)
        ykvod_zhifubao_total=int(cur.fetchone()[0])
        ykvod_zhifubao_fail=ykvod_zhifubao_total - ykvod_zhifubao_success - ykvod_zhifubao_notpay
        if ykvod_zhifubao_total==0:
            ykvod_zhifubao_successrate=100.0
        else:
            ykvod_zhifubao_successrate=100*float(ykvod_zhifubao_success) / float(ykvod_zhifubao_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status in (5,7)' %time_day)
        ykvod_weixin_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status=0' %time_day)
        ykvod_weixin_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2' %time_day)
        ykvod_weixin_total=int(cur.fetchone()[0])
        ykvod_weixin_fail=ykvod_weixin_total - ykvod_weixin_success - ykvod_weixin_notpay
        if ykvod_weixin_total==0:
            ykvod_weixin_successrate=100.0
        else:
            ykvod_weixin_successrate=100*float(ykvod_weixin_success) / float(ykvod_weixin_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status in (5,7)' %time_halfhour_ago)
        ykvod_zhifubao_last30mins_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1 and m.status=0' %time_halfhour_ago)
        ykvod_zhifubao_last30mins_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=1' %time_halfhour_ago)
        ykvod_zhifubao_last30mins_total=int(cur.fetchone()[0])
        ykvod_zhifubao_last30mins_fail=ykvod_zhifubao_last30mins_total - ykvod_zhifubao_last30mins_success - ykvod_zhifubao_last30mins_notpay
        if ykvod_zhifubao_last30mins_total==0:
            ykvod_zhifubao_last30mins_successrate=100.0
        else:
            ykvod_zhifubao_last30mins_successrate=100*float(ykvod_zhifubao_last30mins_success) / float(ykvod_zhifubao_last30mins_total)
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status in (5,7)' %time_halfhour_ago)
        ykvod_weixin_last30mins_success=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2 and m.status=0' %time_halfhour_ago)
        ykvod_weixin_last30mins_notpay=int(cur.fetchone()[0])
        cur.execute('select count(1) from vod.order_info m where m.created_time>%d and m.pay_platform=2' %time_halfhour_ago)
        ykvod_weixin_last30mins_total=int(cur.fetchone()[0])
        ykvod_weixin_last30mins_fail=ykvod_weixin_last30mins_total - ykvod_weixin_last30mins_success - ykvod_weixin_last30mins_notpay
        if ykvod_weixin_last30mins_total==0:
            ykvod_weixin_last30mins_successrate=100.0
        else:
            ykvod_weixin_last30mins_successrate=100*float(ykvod_weixin_last30mins_success) / float(ykvod_weixin_last30mins_total)
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_success, "counterType": "GAUGE", "tags": "platform=zfb,status=success,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_notpay, "counterType": "GAUGE", "tags": "platform=zfb,status=notpay,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_total, "counterType": "GAUGE", "tags": "platform=zfb,status=all,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_fail, "counterType": "GAUGE", "tags": "platform=zfb,status=fail,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_successrate, "counterType": "GAUGE", "tags": "platform=zfb,status=successrate,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_success, "counterType": "GAUGE", "tags": "platform=wx,status=success,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_notpay, "counterType": "GAUGE", "tags": "platform=wx,status=notpay,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_total, "counterType": "GAUGE", "tags": "platform=wx,status=all,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_fail, "counterType": "GAUGE", "tags": "platform=wx,status=fail,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_successrate, "counterType": "GAUGE", "tags": "platform=wx,status=successrate,interval=today"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_last30mins_success, "counterType": "GAUGE", "tags": "platform=zfb,status=success,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_last30mins_notpay, "counterType": "GAUGE", "tags": "platform=zfb,status=notpay,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_last30mins_total, "counterType": "GAUGE", "tags": "platform=zfb,status=all,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_last30mins_fail, "counterType": "GAUGE", "tags": "platform=zfb,status=fail,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_zhifubao_last30mins_successrate, "counterType": "GAUGE", "tags": "platform=zfb,status=successrate,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_last30mins_success, "counterType": "GAUGE", "tags": "platform=wx,status=success,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_last30mins_notpay, "counterType": "GAUGE", "tags": "platform=wx,status=notpay,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_last30mins_total, "counterType": "GAUGE", "tags": "platform=wx,status=all,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_last30mins_fail, "counterType": "GAUGE", "tags": "platform=wx,status=fail,interval=last30mins"})
        counter_list.append({"endpoint": endpoint, "metric": "ykvod.order", "timestamp": ts, "step": step, "value": ykvod_weixin_last30mins_successrate, "counterType": "GAUGE", "tags": "platform=wx,status=successrate,interval=last30mins"})
    else:
        logging.error("can not check order in this server!")

    cur.close()
    conn.close()
except MySQLdb.Error,e:
    logging.error("Mysql Error %d: %s" %(e.args[0], e.args[1]))
    sys.exit(3)

print json.dumps(counter_list)
