#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
import os
import argparse
import ConfigParser

parser = argparse.ArgumentParser(description='aws ec2 instance listing tools.')
parser.add_argument('--region', action='store', help='region help')
parser.add_argument('--profile', action='store', help='profile help')
args = parser.parse_args()

profile = args.profile
region = args.region

home = os.environ.get('HOME')
credentials = home + '/.aws/credentials'

key_pair = ConfigParser.SafeConfigParser() 
key_pair.read(credentials)

access_key = key_pair.get(profile, 'aws_access_key_id')
secret_key = key_pair.get(profile, 'aws_secret_access_key')

client = boto3.client('ec2', region_name = region, aws_access_key_id = access_key, aws_secret_access_key = secret_key)

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
