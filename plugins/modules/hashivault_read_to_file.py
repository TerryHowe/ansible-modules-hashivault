#!/usr/bin/env python
ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_read_to_file
version_added: "3.8.3"
short_description: Hashicorp Vault read module
description:
    - "Reads and deocdes a base64 encoded file from Hashicorp Vault and saves it to disk. Implementation in\
     `/plugins/action/hashivault_read_to_file.py`."
options:
    secret:
        description:
            - vault secret to read.
    key:
        description:
            - secret key/name of file to read from vault.
    dest:
        description:
            - fully qualified path name of file to write to remote host.
    force:
        description:
            - force overwrite of file.
        default: false
    mode:
        description:
            - file permissions of file to write on remote host.
            - in octal, don't forget leading zero!
        default: 0664
    base64:
        description:
            - Secret is base64 encoded
        default: True
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_read_to_file:
        secret: 'giant'
        key: 'foo.dat'
        dest: '/tmp/foo.dat'
'''
