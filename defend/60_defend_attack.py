#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import commands
import logging
import subprocess
import json
import re
import sys
import ConfigParser
import time

ips_allow=['123.103.91.1-254','203.130.46.1-63','123.103.18.129-158','123.103.17.193-254','123.103.11.225-254','123.103.124.1-254','43.247.101.128-254']
endpoint="default"
logging.basicConfig(level=logging.ERROR,
                    filename='/home/work/open-falcon/agent/plugin/error.log',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
with open('/home/work/open-falcon/agent/cfg.json','r') as f:
    json_file=json.loads(f.read())
    endpoint=json_file['hostname']
ip=endpoint.split('_')[0]
#切换目录
try:
    os.chdir(r'/home/work/open-falcon/conf')
except Exception,e:
    logging.error(str(e))
    sys.exit(3)
#判断配置文件是否存在
if not os.path.exists(r'args.conf'):
    logging.error('args.conf is not exists!')
    sys.exit(4)
#获取参数值
cf = ConfigParser.ConfigParser()
cf.read(r'args.conf')
if 'defend_attack' not in cf.sections():
    logging.error('Config section wrong!')
    sys.exit(9)
for item in cf.items('defend_attack'):
    if item[0] == 'synrecv':
        synrecv_limit = int(item[1])
    elif item[0] == 'lastack':
        lastack_limit = int(item[1])
    elif item[0] == 'estab':
        estab_limit = int(item[1])
    else:
        logging.error('para must be "synrecv" and "lastack" and "estab" and "total".')
        sys.exit(5)

#获取SYN_RECV,LAST_ACK,ESTAB,total统计情况
try:
    syn_recv_iter=(line for line in commands.getoutput("ss -ant | grep -E ':80 \|:443 ' | grep 'SYN-RECV' | awk '{print $5}' |awk -F':' '{print $1}' |sort |uniq -c").split('\n')) 
    lastack_iter=(line for line in commands.getoutput("ss -ant | grep -E ':80 \|:443 ' | grep 'LAST-ACK' | awk '{print $5}' |awk -F':' '{print $1}' |sort |uniq -c").split('\n'))
    estab_iter=(line for line in commands.getoutput("ss -ant | grep ':80 \|:443 ' | grep 'ESTAB' | awk '{print $5}' |awk -F':' '{print $1}' |sort |uniq -c").split('\n'))
   

except Exception,e:
    logging.error(str(e))
    sys.exit(6)

#白名单过滤
def IPs_allow(ip,ips):
    tag=False
    ip_sections=ip.split('.')
    for ips_ip in ips:
        ips_sections=ips_ip.split('.')
        if (ip_sections[0]==ips_sections[0] and ip_sections[1]==ips_sections[1] and ip_sections[2]==ips_sections[2] and int(ip_sections[3])>=int(ips_sections[3].split('-')[0]) and int(ip_sections[3])<=int(ips_sections[3].split('-')[1])) or (ip_sections[0]=='192' and ip_sections[1]=='168'):
            tag=True
            break
    return tag
 
#筛选出可疑IP
synrecv_ip = []
lastack_ip = []
estab_ip = []
#total_ip = []

for line in syn_recv_iter:
    if line and int(line.split()[0]) > synrecv_limit and not IPs_allow(line.split()[1],ips_allow):
        synrecv_ip.append({line.split()[1]:line.split()[0]})

for line in lastack_iter:
    if line and int(line.split()[0]) > lastack_limit and not IPs_allow(line.split()[1],ips_allow):
        lastack_ip.append({line.split()[1]:line.split()[0]})

for line in estab_iter:
    if line and int(line.split()[0]) > estab_limit and not IPs_allow(line.split()[1],ips_allow):
        estab_ip.append({line.split()[1]:line.split()[0]})


#通过ipset进行自动化封禁并告警通知管理员
ts=int(time.time())
step=60
counter_list=[]

if subprocess.call('service iptables status &>/dev/null',shell=True):
    logging.error('iptables need installed and started!')
    sys.exit(7)
if subprocess.call('which ipset &>/dev/null',shell=True):
    logging.error('ipset need installed!')
    sys.exit(7)

if not commands.getoutput('ipset list'):
    if subprocess.call('ipset create attackip hash:ip hashsize 4096 maxelem 1000000 timeout 1800 &>/dev/null',shell=True):
        logging.error('ipset create attackip failed!')
        sys.exit(7)
    if 'attackip' not in commands.getoutput('iptables -nL'):
        if subprocess.call('iptables -I INPUT -m set --match-set attackip src -j DROP &>/dev/null',shell=True):
            logging.error('iptables add set attackip failed!')
            sys.exit(7)
if synrecv_ip:
    for ip in synrecv_ip:
        if subprocess.call('ipset add attackip %s &>/dev/null' %ip.keys()[0],shell=True):
            logging.error('Attack IP:%s ipset failed!' %ip.keys()[0])
        else:
            counter_list.append({"endpoint":endpoint,"metric":'attack.ip',"tags":'tcp_status_type=syn_recv,ip=%s' %ip.keys()[0],"timestamp":ts,"step":step,"counterType":"GAUGE","value":'%s' %ip.values()[0]})

if lastack_ip:
    for ip in lastack_ip:
        if subprocess.call('ipset add attackip %s &>/dev/null' %ip.keys()[0],shell=True):
            logging.error('Attack IP:%s ipset failed!' %ip.keys()[0])
        else:
            counter_list.append({"endpoint":endpoint,"metric":'attack.ip',"tags":'tcp_status_type=last_ack,ip=%s' %ip.keys()[0],"timestamp":ts,"step":step,"counterType":"GAUGE","value":'%s' %ip.values()[0]})

if estab_ip:
    for ip in estab_ip:
        if subprocess.call('ipset add attackip %s &>/dev/null' %ip.keys()[0],shell=True):
            logging.error('Attack IP:%s ipset failed!' %ip.keys()[0])
        else:
            counter_list.append({"endpoint":endpoint,"metric":'attack.ip',"tags":'tcp_status_type=estab,ip=%s' %ip.keys()[0],"timestamp":ts,"step":step,"counterType":"GAUGE","value":'%s' %ip.values()[0]})


print json.dumps(counter_list)
