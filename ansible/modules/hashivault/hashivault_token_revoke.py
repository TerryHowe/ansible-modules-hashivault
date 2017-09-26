#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_token_revoke
version_added: "3.3.0"
short_description: Hashicorp Vault token create module
description:
    - Module to revoke tokens in Hashicorp Vault.
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
    revoke_token:
        description:
            - token to be revoked
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - name: "Revoke token"
      hashivault_token_revoke:
        revoke_token: "{{token_to_revoked}}"
      register: "vault_token_revoke_status"
'''


def main():
    argspec = hashivault_argspec()
    argspec['revoke_token'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_token_revoke(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_token_revoke(params):
    client = hashivault_auth_client(params)
    token = params.get('revoke_token')

    client.revoke_token(token, orphan=False, accessor=False)
    return {'changed': True}

if __name__ == '__main__':
    main()
