#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_secret_enable
version_added: "2.2.0"
short_description: Hashicorp Vault secret enable module
description:
    - Module to enable secret backends in Hashicorp Vault.
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
    name:
        description:
            - name of secret backend
    backend:
        description:
            - type of secret backend
    description:
        description:
            - description of secret backend
    config:
        description:
            - config of secret backend
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_secret_enable:
        name: "ephemeral"
        backend: "generic"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['backend'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    argspec['config'] = dict(required=False, type='dict')
    module = hashivault_init(argspec)
    result = hashivault_secret_enable(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_secret_enable(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    backend = params.get('backend')
    description = params.get('description')
    config = params.get('config')
    client.enable_secret_backend(backend, description=description, mount_point=name, config=config)
    return {'changed': True}


if __name__ == '__main__':
    main()
