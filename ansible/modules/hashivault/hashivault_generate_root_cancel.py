#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_generate_root_cancel
version_added: "1.3.2"
short_description: Hashicorp Vault generate_root cancel module
description:
    - Module to cancel generation of root token of Hashicorp Vault.
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
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_generate_root_cancel:
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_generate_root_cancel(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_generate_root_cancel(params):
    client = hashivault_client(params)
    # Check if generate_root is on-going & return when generate_root not in progress
    status = client.generate_root_status
    if not status['started']: 
        return {'changed': False}
    return {'status': client.cancel_generate_root(), 'changed': True}

if __name__ == '__main__':
    main()
