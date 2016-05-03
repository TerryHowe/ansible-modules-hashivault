#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_write
version_added: "0.1"
short_description: Hashicorp Vault write module
description:
    - Module to write to Hashicorp Vault.
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
    secret:
        description:
            - secret to read.
        default: False
    data:
        description:
            - Keys and values to write.
        default: False
    update:
        description:
            - Update rather than overwrite.
        default: False
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_write:
        secret: giant
        data:
            foo: foe
            fie: fum
'''


def main():
    module = hashivault_init(False)
    result = hashivault_write(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *

if __name__ == '__main__':
    main()
