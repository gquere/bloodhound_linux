Bloodhound for Linux
====================

Ingest a dumped OpenLDAP ldif into neo4j to be visualized in Bloodhound.

![view](/view.png)

Usage:
```
./ldif_to_neo4j.py ./sample.ldif | cypher-shell -u neo4j -p password
```

Warning
-------
This script will WIPE the neo4j database before writing to it.

Notes
-----
Could require heavy modifications depending on the LDAP data.

Read more on the [dedicated blogpost](https://www.errno.fr/BloodhoundForLinux.html)

Dependencies
------------
python3-ldap
****NOT**** python3-ldap3
