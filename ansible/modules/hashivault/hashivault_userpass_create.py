#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_userpass_create
version_added: "2.2.0"
short_description: Hashicorp Vault userpass create module
description:
    - Module to create userpass users in Hashicorp Vault.
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
    name:
        description:
            - user name to create.
        default: False
    pass:
        description:
            - user to create password.
        default: False
    policies:
        description:
            - user policies.
        default: default
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_userpass_create:
      name: 'bob'
      pass: 'S3cre7s'
      policies: 'bob'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['pass'] = dict(required=True, type='str')
    argspec['policies'] = dict(required=False, type='str', default='default')
    module = hashivault_init(argspec)
    result = hashivault_userpass_create(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_userpass_create(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    password = params.get('pass')
    policies = params.get('policies')
    client.create_userpass(name, password, policies)
    return {'changed': True}


if __name__ == '__main__':
    main()
