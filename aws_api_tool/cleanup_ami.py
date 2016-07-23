#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import yaml
import boto3

def __format_image_info(images):
  image_info = {}
  for image in images['Images']:
    image_id = image['ImageId']
    snapshot_list = []
    for snapshot_id in image['BlockDeviceMappings']:
      snapshot_list.append(snapshot_id['Ebs']['SnapshotId'])
    image_info[image_id] = snapshot_list

  return image_info

def __print_image_info(image_info):
  for image_id in sorted(image_info.keys()):
    print "imageid : " + image_id
    for snapshot_id in image_info[image_id]:
      print "  snapshotid : " + snapshot_id

def __delete_image(image_info):
  for ami in image_info.keys():
    ec2 = boto3.resource('ec2')
    image = ec2.Image(ami)
    print "delete : " + ami
    image.deregister(DryRun=False)

    snapshot_list = image_info[ami]
    for snapshot_id in snapshot_list:
      snapshot = ec2.Snapshot(snapshot_id)
      print "  delete : " + snapshot_id
      snapshot.delete(DryRun=False)

parser = argparse.ArgumentParser(description='aws ami delete tool.')
group  = parser.add_mutually_exclusive_group()
group.add_argument('--image_id', action='append', help='Remove the specified AMI')
group.add_argument('--image_ids_file', action='store', help='The file you specify the AMI to be deleted. File format is YAML. And Key is \'image_ids\'')
parser.add_argument('--dry_run', dest='dry_run', action='store_true', help='dry_run help')
parser.add_argument('--owner', action='append', default=['self'], help='Choose aws\'s owner. Default value is \'self\'')
parser.add_argument('--profile', action='store', help='Choose aws\'s user profile. This option is not necessary, Once you have set the configuration of awscli(The tool choose default profile)')
parser.add_argument('--region', action='store', help='Choose aws\'s region. This option is not necessary, Once you have set the configuration of awscli(The tool choose default region)')
args = parser.parse_args()

dry_run = args.dry_run
owners  = args.owner
profile = args.profile
region  = args.region

if args.image_id != None:
  image_id = args.image_id
  image_ids = image_id

if args.image_ids_file != None:
  if os.path.isfile(args.image_ids_file):
    image_ids_file = args.image_ids_file
    yaml_data      = yaml.load(open(image_ids_file, 'r'))
    image_ids_yaml = yaml_data['image_ids']
    image_ids      = image_ids_yaml
  else:
    print "Error : image_ids_file is not found."
    sys.exit(1)

session = boto3.session.Session(profile_name = profile, region_name = region)
client = session.client('ec2')
images = client.describe_images(DryRun = False, ImageIds = image_ids, Owners = owners)

if dry_run:
  image_info = __format_image_info(images)
  __print_image_info(image_info)
else:
  image_info = __format_image_info(images)
  __delete_image(image_info)
