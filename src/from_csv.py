#!/usr/bin/python3


import os
import sys
import time
import datetime
import traceback


# Get the Mac and DB classes
from db import Mac, DB


# The name of the couchdb database where I keep my MAC address info
# Must contain only lowercase (a-z), digits (0-9), and _, $, (, ), +, -, and /
# and must begin with a letter.
MAC_DATABASE_NAME = 'macs'


# Selective debug output
DEBUG = False
def debug (msg):
  if DEBUG: print(msg)


# Read the CSV file and pump documents into the DB
if __name__ == '__main__':

  # Check arguments and emit usage message if appropriate
  if 1 != len(sys.argv[1:]) or '-h' != sys.argv[1]:
    print('Usage:')
    print('  ' + sys.argv[0] + '  filename')
    print('Environment environment variables used by this script:')
    print('  MY_COUCHDB_CLIENT_ADDRESS  Address clients can use to connect')
    print('  MY_COUCHDB_HOST_PORT       Host port where container will bind')
    print('  MY_COUCHDB_USER            Admin user name for this instance')
    print('  MY_COUCHDB_PASSWORD        Admin password for this instance')
    sys.exit()
  filepath = sys.argv[1]

  # Requires these things in the environment
  MY_COUCHDB_CLIENT_ADDRESS  = os.environ['MY_COUCHDB_CLIENT_ADDRESS']
  MY_COUCHDB_HOST_PORT       = int(os.environ['MY_COUCHDB_HOST_PORT'])
  MY_COUCHDB_USER            = os.environ['MY_COUCHDB_USER']
  MY_COUCHDB_PASSWORD        = os.environ['MY_COUCHDB_PASSWORD']

  # Connect to the DB
  database_name = MAC_DATABASE_NAME
  db = DB( \
    MY_COUCHDB_CLIENT_ADDRESS,
    MY_COUCHDB_HOST_PORT,
    MY_COUCHDB_USER,
    MY_COUCHDB_PASSWORD,
    database_name)

  # Read tthe file and create or update MAC entries
  f = open(filepath, 'r')
  n = 0
  while True:
    line = f.readline().strip()
    if not line:
        break
    n += 1
    tokens = line.split(',')
    MAC  = tokens[0]
    WE   = tokens[1]
    code = tokens[2]
    info = tokens[3]
    debug('{ "MAC":"' + MAC + '", "WE":"' + WE + '", "code":"' + code + '", "info":"' + info + '" }')
    db.put(MAC, Mac.new_mac(MAC, WE, code, info))
  f.close()

  # Summarize
  print('Processed ' + str(n) + ' entries.')

