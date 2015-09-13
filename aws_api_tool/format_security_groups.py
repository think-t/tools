#!/usr/bin/python
# Author : think-t
# Blog : http://think-t.hatenablog.com

import boto.ec2

region = <designate region>
access_key = <designate your aws acces key>
secret_key = <designate your aws secret key>

header = "security_group_id,security_group_name,mode,protocol,range,from_port,to_port"

def format_security_group_rule(mode, rule_set):
  rule_list = []
  for rule in rule_set:
    range     = str(rule.grants[0])
    protocol  = rule.ip_protocol
    from_port = ''
    to_port   = ''

    if protocol == "-1":
      protocol  = 'all'
      from_port = '0'
      to_port   = '65535'
    else:
      from_port = rule.from_port
      to_port   = rule.to_port

    str_tmp = []
    str_tmp.append(mode)
    str_tmp.append(protocol)
    str_tmp.append(range)
    str_tmp.append(from_port)
    str_tmp.append(to_port)
    rule_list.append(','.join(str_tmp))

  return rule_list

def format_security_group(security_group_id, security_group_name, ingress_rules, egress_rules):
  rule_set = []

  if len(ingress_rules) >= 1:
    for ingress in ingress_rules:
      line = [security_group_id, security_group_name, ingress]
      rule_set.append(','.join(line))

  if len(egress_rules) >= 1:
    for egress in egress_rules:
      line = [security_group_id, security_group_name, egress]
      rule_set.append(','.join(line))

  return rule_set

connection       = boto.ec2.connect_to_region(region, aws_access_key_id = access_key, aws_secret_access_key = secret_key)
security_groups  = connection.get_all_security_groups()

sg_result = {}
for security_group in security_groups:
  ingress_rules = format_security_group_rule('ingress', security_group.rules)
  egress_rules  = format_security_group_rule('egress', security_group.rules_egress)
  sg_result[security_group.id] = format_security_group(security_group.id, security_group.name, ingress_rules, egress_rules)

print header
for key in sorted(sg_result.keys()):
  for rule in sg_result[key]:
    print rule
