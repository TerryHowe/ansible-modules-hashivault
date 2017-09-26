#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_generate_root_init
version_added: "1.3.2"
short_description: Hashicorp Vault generate root token init module
description:
    - Module to start root token generation of Hashicorp Vault.
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
            - "authentication type to use: token, userpass, github, ldap"
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
        default: False
    password:
        description:
            - password to login to vault.
        default: False
    secret_shares:
        description:
            - specifies the number of shares to split the master key into.
        default: 5
    secret_threshold:
        description:
            - specifies the number of shares required to reconstruct the master key.
        default: 3
    pgp_key:
        description:
            - specifies PGP public keys used to encrypt the output root token.
        default: pgp key
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_generate_root_init:
        pgp_key: key
'''

def main():
    argspec = hashivault_argspec()
    argspec['pgp_key'] = dict(required=False, type='str', default='')
    module = hashivault_init(argspec)
    result = hashivault_generate_root_init(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)

from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_generate_root_init(params):
    client = hashivault_client(params)
    # Check if rekey is on-going
    status = client.generate_root_status
    if status['started']: 
        return {'changed': False}
    pgp = params.get('pgp_key')
    return {'status': client.start_generate_root(pgp, otp=False), 'changed': True}

if __name__ == '__main__':
    main()
