from pymongo import MongoClient
from socket import gethostname, gethostbyname

connection_string = ""
with open("connection_string.txt") as connection_string_file:
    for line in connection_string_file:
        connection_string = line

if connection_string is not "":
    client = MongoClient(connection_string)
    replset_config = client.local.system.replset.find_one()
    new_member_id = 0
    for replset_member in replset_config['members']:
        if replset_member['_id'] > new_member_id:
            new_member_id = replset_member['_id']
    new_member_id = new_member_id + 1
    new_member_hostname = gethostbyname(gethostname()) + ':27017'
    replset_config['members'].append({u'host': new_member_hostname, u'_id': new_member_id})
    replset_config['version'] = replset_config['version'] + 1
    client.admin.command({'replSetReconfig': replset_config}, force = False)
