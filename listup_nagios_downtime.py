#!/usr/bin/python
# Author : think-t
# Blog : http://think-t.hatenablog.com
import os
import pynag.Model
import pynag.Parsers
import pynag.Utils
import sys
import time

monitor_host_name = '%s' % os.uname()[1]

icinga_cfg='/usr/local/icinga/etc/icinga.cfg'

status = pynag.Parsers.status(cfg_file=icinga_cfg)
status.parse()
downtimes = []
downtimes += status.data.get('servicedowntime', [])

downtime_list = []
for downtime in xrange(len(downtimes)):
    host_name           = downtimes[downtime]['host_name']
    service_description = downtimes[downtime]['service_description']
    start_time          = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(downtimes[downtime]['start_time'])))
    end_time            = time.strftime("%Y/%m/%d %H:%M:%S" ,time.localtime(float(downtimes[downtime]['end_time'])))
    line = monitor_host_name + ',' + host_name + ',' + service_description + ',' + start_time + ',' + end_time
    downtime_list.append(line)

for line in downtime_list:
    print line
