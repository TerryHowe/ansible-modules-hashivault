#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_generate_root
version_added: "1.2.0"
short_description: Hashicorp Vault generate_root module
description:
    - Module to (update) generate_root Hashicorp Vault.
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
    key:
        description:
            - vault key shard.
        default: False
    nonce:
        description:
            - generate_root nonce.
        default: False
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_generate_root:
      key: '{{vault_unseal_key}}'
      nonce: '{{nonce}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['key'] = dict(required=True, type='str')
    argspec['nonce'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_generate_root(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_generate_root(params):
    key = params.get('key')
    nonce = params.get('nonce')
    client = hashivault_client(params)
    return {'status': client.generate_root(key, nonce), 'changed': True}


if __name__ == '__main__':
    main()
