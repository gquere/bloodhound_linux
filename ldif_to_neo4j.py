#!/usr/bin/env python3
import ldif
import json
import sys

if len(sys.argv) != 2:
    print("usage:")
    print("./ldif_to_neo4j.py ./sample.ldif | cypher-shell -u neo4j -p password")
    exit(1)

with open(sys.argv[1], 'r') as f:
    parser = ldif.LDIFRecordList(f)
    parser.parse()

users = []
groups = []
computers = []
domain = 'sample'
objectid = 3

# This whole parsing block will depend on the structure of your LDAP DB, it probably won't work out of the box
# In the end we need:
#   * a list of users
#   * a list of groups and their associated users
#   * a list of computers and their associated groups
for entry in parser.all_records:
    # users
    if b'inetOrgPerson' in entry[1]['objectClass']:
        distinguishedname = entry[0]
        name = entry[1]['cn'][0].decode().upper()
        displayname = entry[1]['givenName'][0].decode() + ' ' + entry[1]['sn'][0].decode()
        users.append({'distinguishedname':distinguishedname, 'name':name, 'displayname':displayname, 'objectid':objectid})

    # groups
    if b'posixGroup' in entry[1]['objectClass']:
        distinguishedname = entry[0]
        name = entry[1]['cn'][0].decode().upper()
        description = entry[1]['description'][0].decode()
        members = entry[1]['memberUid']
        groups.append({'distinguishedname':distinguishedname, 'name':name, 'description':description, 'members':members, 'objectid':objectid})

    # computers
    if b'Host' in entry[1]['objectClass']:
        distinguishedname = entry[0]
        name = entry[1]['cn'][0].decode().upper()
        sshgroups = entry[1]['memberNisNetgroup']
        computers.append({'distinguishedname':distinguishedname, 'name':name, 'sshgroups':sshgroups, 'objectid':objectid})

    objectid+=1


# Wipe the current DB
print('MATCH (n) DETACH DELETE n;')

# Create basic OUs
print('CREATE ')
print('(varouuser:OU:Base {{distinguishedname:"ou=users,dc=sample,dc=com", name:"users", objectid:"{}", domain:"{}"}}),'.format(1, domain))
print('(varougroup:OU:Base {{distinguishedname:"ou=groups,dc=sample,dc=com", name:"groups", objectid:"{}", domain:"{}"}}),'.format(2, domain))
print('(varoucomputer:OU:Base {{distinguishedname:"ou=computers,dc=sample,dc=com", name:"computers", objectid:"{}", domain:"{}"}}),'.format(3, domain))

# Then populare each
for user in users:
    print('(var{}:User:Base {{ name:"{}", displayname:"{}", distinguishedname:"{}", description:"{}", domain:"{}", objectid:"{}", highvalue:false, enabled:true}}),'.format(user['name'], user['name'], user['displayname'], user['distinguishedname'], "no description", domain, user['objectid']))
    print('(varouuser)-[:Contains]->(var{}),'.format(user['name']))

for group in groups:
    print('(var{}:Group:Base {{ name:"{}", distinguishedname:"{}", domain:"{}", description:"{}", highvalue:false, admincount:false, objectid:"{}" }}),'.format(group['name'], group['name'], group['distinguishedname'], domain, group['description'], group['objectid']))
    for user in group['members']:
        print('(var{})-[:MemberOf]->(var{}),'.format(user.decode().upper(), group['name']))
    print('(varougroup)-[:Contains]->(var{}),'.format(group['name']))

for computer in computers:
    print('(var{}:Computer:Base {{name:"{}", distinguishedname:"{}", domain:"{}", objectid:"{}", highvalue:false, haslaps:false, operatingsystem:"Linux", unconstraineddelegation:false, enabled:true, owned:false}}),'.format(computer['name'], computer['name'], computer['distinguishedname'], domain, computer['objectid']))
    for group in computer['sshgroups']:
        print('(var{})-[:CanRDP]->(var{}),'.format(group.decode().upper(), computer['name']))
    print('(varoucomputer)-[:Contains]->(var{}),'.format(computer['name']))

print('(var{}:Domain:Base {{ name:"{}", functionallevel:"{}", highvalue:true, distinguishedname:"{}", domain:"{}", objectid:"{}" }} );'.format(domain, domain, '2012', domain, domain, 0))
