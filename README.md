Bloodhound for Linux
====================

Ingest a dumped OpenLDAP ldif into neo4j to be visualized in Bloodhound.

![view](/view.png)

Usage:
```
./ldif_to_neo4j.py ./sample.ldif | cypher-shell -u neo4j -p password
```

Notes
-----
Could require heavy modifications depending on the LDAP data.

Read more at:
