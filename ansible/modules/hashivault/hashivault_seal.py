#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_seal
version_added: "1.2.0"
short_description: Hashicorp Vault seal module
description:
    - Module to seal Hashicorp Vault.
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
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_seal:
      register: 'vault_seal'
    - debug: msg="Seal return is {{vault_seal.rc}}"
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_seal(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_seal(params):
    key = params.get('key')
    client = hashivault_auth_client(params)
    return {'status': client.seal(), 'changed': True}


if __name__ == '__main__':
    main()
