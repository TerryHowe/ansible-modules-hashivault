#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_read_file
version_added: "3.4.2"
short_description: Hashicorp Vault read module
description:
    - Reads and deocdes a base64 encoded file from Hashicorp Vault. Implementation in `/plugins/action/hashivault_read_file.py`.
options:
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    verify:
        description:
            - verify TLS certificate
        default: to environment variable VAULT_SKIP_VERIFY
    authtype:
        description:
            - "authentication type to use: token, userpass, github, ldap, approle"
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
    password:
        description:
            - password to login to vault.
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
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_read_file:
        secret: 'giant'
        key: 'foo.dat'
        dest: '/tmp/foo.dat'
'''