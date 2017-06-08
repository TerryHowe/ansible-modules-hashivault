#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_token_create
version_added: "2.2.0"
short_description: Hashicorp Vault token create module
description:
    - Module to create tokens in Hashicorp Vault.
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
    - hashivault_token_create:
      policies: ['stan', 'kyle']
      lease: '1h'
      orphan: yes
      renewable: yes 
      token: {{ 
'''


def main():
    argspec = hashivault_argspec()
    argspec['lease'] = dict(required=False, type='str', default='1h')
    argspec['role'] = dict(required=False, type='str', default='1h')
    argspec['renewable'] = dict(required=False, type='bool', default=False)
    argspec['orphan'] = dict(required=False, type='bool', default=False)
    argspec['ttl'] = dict(required=False, type='str', default='1h')
    argspec['policies'] = dict(required=True, type='str')
    argspec['display_name'] = dict(required=True, type='str')
    argspec['metadata'] = dict(required=False, type='str')
    argspec['token'] = dict(required=False, type='str')
    module = hashivault_init(argspec)
    result = hashivault_token_create(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_token_create(params):
    client = hashivault_auth_client(params)
    policies = params.get('policies')
    token = client.create_token(policies=policies)
    return {'changed': True, 'token': token}

if __name__ == '__main__':
    main()
