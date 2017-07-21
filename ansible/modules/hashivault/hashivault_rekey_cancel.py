#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_rekey_cancel
version_added: "3.3.0"
short_description: Hashicorp Vault rekey cancel module
description:
    - Module to cancel rekey Hashicorp Vault.
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
    password:
        description:
            - password to login to vault.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_rekey_cancel:
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_rekey_cancel(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_rekey_cancel(params):
    client = hashivault_client(params)
    # Check if rekey is on-going & return when rekey not in progress
    status = client.rekey_status
    if not status['started']: 
        return {'changed': False}
    return {'status': client.cancel_rekey(), 'changed': True}

if __name__ == '__main__':
    main()
