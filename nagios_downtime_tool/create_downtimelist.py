#!/usr/bin/python
# Author : think-t
# Blog : http://think-t.hatenablog.com
import glob

from Cheetah.Template import Template
template = Template(file='/dir/downtime.tmpl')

downtimes = []
for file in glob.glob('/dir/*.log'):
    for line in open(file, 'r'):
        line = line.rstrip()
        list = line.split(',')
        downtimes.append({'monitor_host_name': str(list[0]), 'host_name': str(list[1]), 'service_description': str(list[2]), 'start_time': str(list[3]), 'end_time': str(list[4])}) 
template.downtimes = downtimes
print template
