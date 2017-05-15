#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_secret_disable
version_added: "2.2.0"
short_description: Hashicorp Vault secret disable module
description:
    - Module to disable secret backends in Hashicorp Vault.
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
    name:
        description:
            - name of secret backend
        default: False
    backend:
        description:
            - type of secret backend
        default: False
    description:
        description:
            - description of secret backend
        default: False
    config:
        description:
            - config of secret backend
        default: False
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_secret_disable:
        name: "ephemeral"
        backend: "generic"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_secret_disable(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_secret_disable(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    client.disable_secret_backend(name)
    return {'changed': True}


if __name__ == '__main__':
    main()
