#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author：yanwen
#Date：2017.03.31
#Version：1.0
#V1.0 Description：监控广告发送结果是否异常

import sys
import json
import time
import datetime
import os
import re
import urllib2
import logging
import commands
import platform

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

ts=int(time.time())
step=600
counter_list=[]
now = datetime.datetime.now()
delta = datetime.timedelta(days=1)
tomorrow=now+delta
startdate=now.strftime('%Y-%m-%d')
enddate=tomorrow.strftime('%Y-%m-%d')
try:
    re1=commands.getoutput("""mysql -uhitv -phitv case_db -e "select if(rate>=0.95,'normal','exception') as v from (select sum(sendline + sendlinebyfile)/sum(parserline) as rate from appadsendrecord t where 1 = 1 and date_format(date_add(t.startsenddate, interval 8 hour),'%%Y%%m%%d') < replace('%s','-','') and date_format(date_add(t.startsenddate, interval 8 hour),'%%Y%%m%%d') >= replace('%s','-','')) x" 2>/dev/null""" %(enddate,startdate))
    re2=commands.getoutput("""mysql -uhitv -phitv case_db -e "select if(c1=0,'normal','exception') as v from (select count(1) as c1 from (select sum(sendline + sendlinebyfile)/sum(parserline)  as c from appadsendrecord t where 1 = 1 and date_format(date_add(t.startsenddate, interval 8 hour),'%%Y%%m%%d')<replace('%s','-','') and date_format(date_add(t.startsenddate, interval 8 hour),'%%Y%%m%%d') >= replace('%s','-','') group by date_format(date_add(t.startsenddate, interval 8 hour),'%%Y%%m%%d%%H'))x where c < 0.9) y" 2>/dev/null""" %(enddate,startdate))
    re3=commands.getoutput("""mysql -uhitv -phitv case_db -e "select if(dayparameter < nowday && c = 24, 'normal',if(dayparameter = nowday && c = nowh + 1, 'normal','exception')) as v from (select count(distinct cast(date_format(date_add(t.endsenddate, interval 8 hour),'%%H') as signed)) as c,min(cast(date_format(date_add(t.endsenddate, interval 8 hour),'%%H') as signed)) as mmin,max(cast(date_format(date_add(t.endsenddate, interval 8 hour),'%%H') as signed)) as mmax,(select date_format(date_add(now(), interval 8 hour),'%%Y%%m%%d') from dual) as nowday, (select cast(date_format(date_add(now(), interval 8 hour),'%%H') as signed) from dual) as nowh,replace('%s','-','') as dayparameter from appadsendrecord t where 1 = 1 and date_format(date_add(t.endsenddate, interval 8 hour),'%%Y%%m%%d') < replace('%s','-','') and date_format(date_add(t.endsenddate, interval 8 hour),'%%Y%%m%%d') >= replace('%s','-','')) x" 2>/dev/null""" %(startdate,enddate,startdate))
    status1=re1.split("\n")[1]
    status2=re2.split("\n")[1]
    status3=re3.split("\n")[1]
except Exception,e:
    logging.error("Run sql shell error!")
    sys.exit(3)
if "normal" in status1 and "normal" in status2 and "normal" in status3:
    counter_list.append({"endpoint": endpoint, "metric": "adCntResult.status", "timestamp": ts, "step": step, "value": 1, "counterType": "GAUGE", "tags": ""})
else:
    counter_list.append({"endpoint": endpoint, "metric": "adCntResult.status", "timestamp": ts, "step": step, "value": 0, "counterType": "GAUGE", "tags": ""})

print json.dumps(counter_list)

