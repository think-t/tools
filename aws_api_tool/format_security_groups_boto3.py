#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
import argparse

parser = argparse.ArgumentParser(description='aws ec2 securitygroup listing tools.')
parser.add_argument('--region',  action='store',  help='Choose aws\'s region. This option is not necessary, Once you have set the configuration of awscli(The tool choose default region)')
parser.add_argument('--profile', action='store',  help='Choose aws\'s user profile. This option is not necessary, Once you have set the configuration of awscli(The tool choose default profile)')
parser.add_argument('--vpc_id',  action='append', help='Choose aws\'s VPCId.')
args = parser.parse_args()

region  = args.region
profile = args.profile
vpcs    = args.vpc_id

header = "security_group_id,security_group_name,mode,protocol,range,from_port,to_port"

def __format_rule(group_id, group_name, mode, ip_protocol, network, from_port, to_port):
  line = []
  line.append(group_id)
  line.append(group_name)
  line.append(mode)
  line.append(ip_protocol)
  line.append(network)
  line.append(from_port)
  line.append(to_port)
  return line 

def __format_security_group_rule(mode, security_group):
  rule_list = []
  if mode == 'ingress':
    permissions = 'IpPermissions'
  elif mode == 'egress':
    permissions = 'IpPermissionsEgress'

  group_name = str(security_group['GroupName'])
  group_id   = str(security_group['GroupId'])

  for rule in security_group[permissions]:
    ip_protocol = rule['IpProtocol']
    from_port   = ''
    to_port     = ''

    if ip_protocol == "-1":
      ip_protocol  = 'all'
      from_port    = '0'
      to_port      = '65535'
    else:
      from_port = str(rule['FromPort'])
      to_port   = str(rule['ToPort'])

    for ip_range in rule['IpRanges']:
      cidr_ip = ip_range['CidrIp']
      rule_list.append(',' .join(__format_rule(group_id, group_name, mode, ip_protocol, cidr_ip, from_port, to_port)))

    for user_id_group_pair in rule['UserIdGroupPairs']:
      user_id_group = user_id_group_pair['GroupId']
      rule_list.append(',' .join(__format_rule(group_id, group_name, mode, ip_protocol, user_id_group, from_port, to_port)))

  return rule_list

session = boto3.session.Session(profile_name = profile, region_name = region)
client = session.client('ec2')
response = client.describe_security_groups(
  Filters=[
    {
      'Name'   : 'vpc-id',
      'Values' : vpcs 
    }
  ]
)

rule_list = []
for security_group in response['SecurityGroups']:
  rule_list.extend(__format_security_group_rule('ingress', security_group))
  rule_list.extend(__format_security_group_rule('egress', security_group))

print header
for rule in rule_list:
  print rule
