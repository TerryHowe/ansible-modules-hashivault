#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_init
version_added: "2.2.0"
short_description: Hashicorp Vault init enable module
description:
    - Module to init Hashicorp Vault.
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
            - authentication type to use: token, userpass, github, ldap
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
    - hashivault_init:
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_initialize(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_initialize(params):
    client = hashivault_client(params)
    if client.is_initialized():
        return {'changed': False}
    result =  {'changed': True}
    result.update(client.is_initialized())
    return result


if __name__ == '__main__':
    main()
