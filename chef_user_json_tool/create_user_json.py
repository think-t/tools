#!/usr/bin/python
# Author : think-t
# Blog : http://think-t.hatenablog.com
#coding:utf-8

import csv
import codecs
import json
import crypt
import random
import hashlib
import subprocess
import re

csv_file = open('user.csv', 'rb')
reader   = csv.reader(csv_file)

for row in reader:
  user       = row[0]
  uid        = row[1]
  gid        = row[2]
  home       = row[3]
  shell      = row[4]
  password   = row[5]
  passphrase = row[6]
  sudo       = row[7]

  random.seed()
  password_hash = crypt.crypt(password, "$6$" + hashlib.sha512(str(random.random())).hexdigest())
  
  cmd = [ "ssh-keygen", "-b", "2048", "-t", "rsa", "-N", passphrase, "-f", user + ".key" ]
  subprocess.check_call(cmd)

  pubkey = open(user + ".key.pub", 'rb')

  r = re.compile(r'ssh-rsa.*==')
  m = r.search(pubkey.read())
  authorized_keys = m.group(0) + '\n'

  if sudo == 'true':
    sudo_config = user + "    ALL=(ALL)    NOPASSWD: ALL\n"
    record = { "id":user, "uid":uid, "gid":gid, "home":home, "shell":shell, "password":password_hash, "authorized_keys":authorized_keys, "sudo":sudo_config } 
  else:
    record = { "id":user, "uid":uid, "gid":gid, "home":home, "shell":shell, "password":password_hash, "authorized_keys":authorized_keys } 

  jsonfile = codecs.open(user + ".json", "w", "utf-8")
  json.dump(record, jsonfile, sort_keys=True, ensure_ascii=False, indent=2)
