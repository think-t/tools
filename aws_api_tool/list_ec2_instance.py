#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
import os
import argparse

parser = argparse.ArgumentParser(description='aws ec2 instance listing tools.')
parser.add_argument('--region', action='store', help='Choose aws\'s region. This option is not necessary, Once you have set the configuration of awscli(The tool choose default region)')
parser.add_argument('--profile', action='store', help='Choose aws\'s user profile. This option is not necessary, Once you have set the configuration of awscli(The tool choose default profile)')
args = parser.parse_args()

profile = args.profile
region = args.region

session = boto3.session.Session(profile_name = profile, region_name = region)
client = session.client('ec2')

response = client.describe_instances()

print 'NameTag,InstanceId,InstanceType,Platform,AvailabilityZone'

for reservations in response['Reservations']:
  for instances in reservations['Instances']:
    instance_id       = instances['InstanceId']
    instance_type     = instances['InstanceType']
    availability_zone = instances['Placement']['AvailabilityZone']

    platform = 'nodata'
    if instances.has_key('Platform'):
      platform = instances['Platform']

    name_tag = 'nodata'
    if instances.has_key('Tags'):
      for tag in instances['Tags']:
        if tag['Key'] == 'Name':
          name_tag = tag['Value']
    print ','.join([name_tag, instance_id, instance_type, platform, availability_zone])
