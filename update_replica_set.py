from pymongo import MongoClient
from socket import gethostname, gethostbyname
from time import sleep

def get_connection_string_from_file(filename = None):
    '''
    Gets the connection string from a file. 
    Default is connection_string.txt located in the local directory
    Inputs:
        filename: Optional; location to search for connection string
    Returns:
        connection_string: The mongo connection string stored in filename
    '''
    if filename is None:
        filename = "connection_string.txt"
    connection_string = ""
    with open(filename) as connection_string_file:
        for line in connection_string_file: # this will get only the last line
            connection_string = line
    return connection_string

def get_connection_string_from_github(uri = None):
    '''
    Gets the connection string from github.
    Inputs:
        uri: Optional; URI to search for connection string
    Returns:
        connection_string: The mongo connection string stored in filename
    ******NEEDS TO BE FINISHED******
    '''
    if uri is None:
        uri = "https://raw.githubusercontent.com/executivereader/mongo-startup/master/connection_string.txt"
    connection_string = ""
    return connection_string

def start_mongo_client(filename = None, uri = None):
    '''
    Tries to get a MongoClient
    First tries the connection string in the local file
    Next tries the connection string on github
    Inputs:
        filename: Optional; filename to look for connection string in
        uri: Optional; URI to look for connection string in
    '''
    connection_string = get_connection_string_from_file(filename)
    try:
        client = MongoClient(connection_string)
    except Exception:
        connection_string = get_connection_string_from_github(uri)
        client = MongoClient(connection_string)
    return client

def member_of_replica_set(client, hostname = None, port = None):
    '''
    Checks if hostname:port is in the replica set connected to from connection_string
    Inputs:
        client: a MongoClient instance
        hostname: Optional; hostname or IP address (default: socket.gethostbyname(socket.gethostname()))
        port: Optional; defaults to 27017
    Returns:
        True if hostname:port is in the replica set
        False otherwise
    '''
    if hostname is None:
        hostname = gethostbyname(gethostname())
    if port is None:
        port = 27017
    replset_config = client.local.system.replset.find_one()
    for replset_member in replset_config['members']:
        if replset_member['host'] ==  gethostbyname(gethostname()) + ':27017':
            return True
    return False

def get_available_host_id(client):
    '''
    Gets an id that is available for adding a member to a replica set.
    Inputs:
        client: a MongoClient instance
    Returns:
        new_member_id: the smallest integer that is an available id
    '''
    replset_config = client.local.system.replset.find_one()
    new_member_id = 1
    id_not_ok = True
    while id_not_ok:
        id_not_ok = False
        for replset_member in replset_config['members']:
            if replset_member['_id'] == new_member_id:
                new_member_id = new_member_id + 1
                id_not_ok = True
    return new_member_id

def add_member_to_replica_set(client, hostname = None, port = None, force = None):
    '''
    Adds a member to the replica set. 
    Will not add if the hostname is already in the replset.
    Inputs: 
        client: a MongoClient instance
        hostname: Optional; hostname or IP address (default socket.gethostbyname(socket.gethostname()))
        port: Optional; defaults to 27017
        force: Optional; defaults to False
    Returns:
        True if hostname:port appears in the replica set configuration after the function runs
        False otherwise
    '''
    if hostname is None:
        hostname = gethostbyname(gethostname())
    if port is None:
        port = 27017
    if force is None:
        force = False
    new_member_hostname = hostname + ':' + str(port)
    if not member_of_replica_set(client,hostname,port):
        replset_config = client.local.system.replset.find_one()
        replset_config['members'].append({u'host': hostname + ':' + str(port), u'_id': get_available_host_id(client)})
        replset_config['version'] = replset_config['version'] + 1
        client.admin.command({'replSetReconfig': replset_config}, force = force)
    return member_of_replica_set(client,hostname,port)

def get_connection_string(client, options = None):
    '''
    Gets a connection string that will work for an existing replica set
    Inputs:
        client: a MongoClient instance
        options: Optional; string to add to the end of the connection string
    '''
    connection_string = "mongodb://"
    replset_status = client.admin.command({'replSetGetStatus': 1})
    num_members = 0
    for replset_member in replset_status['members']:
        if num_members == 0:
            connection_string = connection_string + ","
        connection_string = connection_string + replset_member['name']
        num_members = num_members + 1
    connection_string = connection_string + "/?replicaSet=" + replset_status['set']
    if options is not None:
        connection_string = connection_string + "&" + options
    return connection_string

# now add myself to the replica set
max_tries = 3
client = start_mongo_client()
idx = 0
while idx < max_tries:
    try:
        add_member_to_replica_set(client)
    except Exception:
        pass
    idx = idx + 1
if member_of_replica_set(client):
    print "Successfully added myself to replica set on try " + str(idx)
    # consider updating connection string here
    connection_string = get_connection_string(client)
    print "New connection string is:\n" + connection_string
    # sleep(120)
    # now delete any members that are in an unreachable status
    if connection_string is not "":
        print "Reconnecting to " + connection_string
        client = MongoClient(connection_string)
        replset_status = client.admin.command({'replSetGetStatus': 1})
        if replset_status['ok'] == 1.0: # don't delete any members if the replica set is not in a healthy status
            print "Replica set ok, deleting old members one by one"
            print "******MORE TO DO HERE******"
else:
    print "Failed to add myself to replica set after " + str(idx) + " tries"
