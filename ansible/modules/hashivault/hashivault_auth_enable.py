#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_auth_enable
version_added: "2.2.0"
short_description: Hashicorp Vault auth enable module
description:
    - Module to enable authentication backends in Hashicorp Vault.
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
            - name of authenticator
        default: False
    description:
        description:
            - description of authenticator
        default: False
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_enable:
        name: "userpass"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    module = hashivault_init(argspec)
    result = hashivault_auth_enable(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_auth_enable(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    description = params.get('description')
    client.enable_auth_backend(name, description=description)
    return {'changed': True}


if __name__ == '__main__':
    main()
