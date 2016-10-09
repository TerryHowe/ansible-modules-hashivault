#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_policy_list
version_added: "2.1.0"
short_description: Hashicorp Vault policy list module
description:
    - Module to list policies in Hashicorp Vault.
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
    - hashivault_policy_list:
      register: 'vault_policy_list'
    - debug: msg="Policies are {{vault_policy_list.policy}}"
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_policy_list(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_policy_list(params):
    client = hashivault_auth_client(params)
    return {'policies': client.list_policies()}


if __name__ == '__main__':
    main()
