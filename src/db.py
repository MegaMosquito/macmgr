#!/usr/bin/python3


import os
import sys
import time
import datetime
import traceback


# Selective debug output
DEBUG_INIT    = False
DEBUG_GET     = False
DEBUG_PUT     = False
DEBUG_DELETE  = False
DEBUG_TEST    = False
def debug (flag, msg):
  if flag: print(msg)


# Don't forget to `pip install couchdb`
import couchdb


# Global for the server handle (only needed to remove the DB in the test code
couchdbserver = None


# A simple class for MAC address objects with info fields
class Mac:

  # Generic pseudo-constructor
  #   MAC:   MAC address (the key)
  #   WE:    W (wifi) or E (wired Ethernet)
  #   code:  Host type code:
  #            RPi   Any Raspberry Pi model
  #            APi   Intel Atom-based Atomic Pi
  #            OPi   Orange Pi
  #            NVD   Any NVIDIA Jetson model
  #            APL   Any Apple product
  #            AMZ   Any Amazon product
  #            iPC   An Intel-based PC (running Windows)
  #            OTH   Anything else
  #   info:  Free form descriptive text for this host
  @staticmethod
  def new_mac(MAC, WE, code, info):
    mac = dict()
    mac['_id'] = MAC.upper()
    mac['MAC'] = MAC.upper()
    mac['WE'] = WE
    mac['code'] = code
    mac['info'] = info
    return mac

  # Static method for copying
  @staticmethod
  def copy(dest, src):
    dest['MAC']  = src['MAC'].upper()
    dest['WE']   = src['WE']
    dest['code'] = src['code']
    dest['info'] = src['info']

  # Static method for JSON stringification
  @staticmethod
  def to_json_str(mac):
    return('{ ' + \
      '"_id": "' + mac['_id'] + '"' + \
      ', "MAC": "' + mac['MAC'] + '"' + \
      ', "WE": "' + mac['WE'] + '"' + \
      ', "code": "' + mac['code'] + '"' + \
      ', "info": "' + mac['info'] + '"' + \
      ' }')


# A class for our database of "Mac" documents
class DB:

  def __init__(self, address, port, user, password, database):
    self.db = None
    self.name = database
    global couchdbserver

    # Try forever to connect
    while True:
      debug(DEBUG_INIT, 'Attempting to connect to CouchDB server at ' + address + ':' + str(port) + '...')
      couchdbserver = couchdb.Server('http://%s:%s@%s:%d/' % ( \
        user, \
        password, \
        address, \
        port))
      if couchdbserver:
        break
      debug(DEBUG_INIT, 'CouchDB server not accessible. Will retry...')
      time.sleep(10)

    # Connected!
    debug(DEBUG_INIT, 'Connected to CouchDB server.')

    # Open or create our database
    debug(DEBUG_INIT, 'Attempting to open the "' + database + '" DB...')
    if database in couchdbserver:
      self.db = couchdbserver[database]
    else:
      self.db = couchdbserver.create(database)

    # Done!
    debug(DEBUG_INIT, 'CouchDB database "' + database + '" is open and ready for use.')
    sys.stdout.flush()

  # Instance method to get all the DB "Mac" documents
  def get_all_docs(self):
    def sort_key(doc):
      return doc['MAC'] 
    docs = []
    for row in self.db.view('_all_docs'):
      docs.append(self.db[row.key])
    return sorted(docs, key=sort_key)

  # Instance method to read a "Mac" document using MAC as '_id'
  def get(self, MAC):
    debug(DEBUG_GET, 'DB.get("' + MAC + '")')
    doc = None
    try:
      MAC = MAC.upper()
      doc = self.db.get(MAC)
      if doc:
        debug(DEBUG_GET, 'DB.get():     MAC="' + MAC + '" <-- ' + Mac.to_json_str(doc))
        return doc
    except Exception as e:
      print('*** Exception during DB.get("' + MAC + '"):')
      traceback.print_exc()
    debug(DEBUG_GET, 'DB.get():     MAC="' + MAC + '" *** NOT FOUND! ***')
    doc = None
    return doc

  # Instance method to write a "Mac" document (MAC as '_id' plus other fields)
  def put(self, MAC, mac):
    debug(DEBUG_PUT, 'DB.put("' + MAC + '","' + Mac.to_json_str(mac) + '")')
    doc = None
    try:
      MAC = MAC.upper()
      # Does it exist in the DB already?
      doc = self.get(MAC)
    except Exception as e:
      print('*** Exception during DB.put("' + MAC + '"):')
      traceback.print_exc()
    if doc:
      debug(DEBUG_PUT, 'DB.put():     MAC="' + MAC + '" <-- ' + Mac.to_json_str(doc))
      
      Mac.copy(doc, mac)
      self.db[MAC] = doc
    else:
      self.db.save(mac)
    debug(DEBUG_PUT, 'DB.put():     MAC="' + MAC + '" ==> ' + Mac.to_json_str(mac))

  # Instance method to delete a "Mac" document using MAC as '_id'
  def delete(self, MAC):
    debug(DEBUG_DELETE, 'DB.delete("' + MAC + '")')
    doc = None
    try:
      MAC = MAC.upper()
      doc = self.db.get(MAC)
      if doc:
        debug(DEBUG_DELETE, 'DB.delete():  MAC="' + MAC + '" *X* ' + Mac.to_json_str(doc))
        self.db.delete(doc)
        return
    except Exception as e:
      print('*** Exception during DB.delete("' + MAC + '"):')
      traceback.print_exc()
    debug(DEBUG_DELETE, 'DB.delete():  MAC="' + MAC + '" *** NOT FOUND! ***')

  # Instance method for stringification
  def __str__(self):
    return 'DB( name:"' + self.name + '", docs:' + str(len(self.get_all())) + ' )'

  # Instance method to get the size (number of docs) of the database
  def size(self):
    return len(self.get_all())

  # Instance method to wipe all documents from the DB
  def clean(self):
    rows = self.db.view('_all_docs', include_docs=True)
    docs = []
    for row in rows:
      if row['id'].startswith('_'):
        continue
      doc = row['doc']
      doc['_deleted'] = True
      docs.append(doc)
    self.db.update(docs)

  # Instance method to wipe DB from couchdb, and disable this object
  def terminate(self):
    # First remove all the documents
    self.clean()
    # Then remove the empty database
    del couchdbserver[self.name]
    # Then sabotage this object so it can no longer be used
    self.db = None

# A basic test shell for this module
if __name__ == '__main__':

  # Requires these things in the environment
  MY_COUCHDB_CLIENT_ADDRESS  = os.environ['MY_COUCHDB_CLIENT_ADDRESS']
  MY_COUCHDB_HOST_PORT       = int(os.environ['MY_COUCHDB_HOST_PORT'])
  MY_COUCHDB_USER            = os.environ['MY_COUCHDB_USER']
  MY_COUCHDB_PASSWORD        = os.environ['MY_COUCHDB_PASSWORD']

  print('Executing self-test....')
  database_name = 'test-db'

  # Instantiate the db object (i.e., connect to CouchDB, and open our DB)
  db = DB( \
    MY_COUCHDB_CLIENT_ADDRESS,
    MY_COUCHDB_HOST_PORT,
    MY_COUCHDB_USER,
    MY_COUCHDB_PASSWORD,
    database_name)

  # Clean
  debug(DEBUG_TEST, 'Clean:')
  db.clean()
  assert db.size() == 0

  # Put/Get
  debug(DEBUG_TEST, 'Put/Get:')
  k = '00:00:00:00:00:00'
  db.put(k, Mac.new_mac(k, 'E', 'OTH', 'foo'))
  assert db.size() == 1
  d = db.get(k)
  assert d['info'] == 'foo'

  # Delete
  debug(DEBUG_TEST, 'Delete:')
  k = '00:00:00:00:00:00'
  db.delete(k)
  assert db.size() == 0
  d = db.get(k)
  assert d is None

  # Update
  debug(DEBUG_TEST, 'Update:')
  k = '00:00:00:00:00:00'
  db.put(k, Mac.new_mac(k, 'E', 'OTH', 'foo'))
  assert db.size() == 1
  k2 = '00:00:00:00:00:01'
  db.put(k2, Mac.new_mac(k2, 'E', 'OTH', 'bar'))
  assert db.size() == 2
  db.put(k, Mac.new_mac(k, 'E', 'OTH', 'foo2'))
  assert db.size() == 2
  d = db.get(k)
  assert d['info'] == 'foo2'

  # More
  debug(DEBUG_TEST, 'More:')
  k = '00:00:00:00:00:02'
  db.put(k, Mac.new_mac(k, 'E', 'OTH', 'baz'))
  assert db.size() == 3
  k = '00:00:00:00:00:03'
  db.put(k, Mac.new_mac(k, 'E', 'OTH', 'whiz'))
  assert db.size() == 4
  k = '00:00:00:00:00:04'
  db.put(k, Mac.new_mac(k, 'E', 'OTH', 'wazoo'))
  assert db.size() == 5

  # Cleanup
  debug(DEBUG_TEST, 'Cleanup:')
  db.terminate()
  assert not (database_name in couchdbserver)

  print('All tests completed successfully.')


