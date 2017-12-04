#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_unseal
version_added: "1.2.0"
short_description: Hashicorp Vault unseal module
description:
    - Module to unseal Hashicorp Vault.
options:
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    ca_cert:
        description:
            - "path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate"
        default: to environment variable VAULT_CACERT
    ca_path:
        description:
            - "path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate : if ca_cert is specified, its value will take precedence"
        default: to environment variable VAULT_CAPATH
    client_cert:
        description:
            - "path to a PEM-encoded client certificate for TLS authentication to the Vault server"
        default: to environment variable VAULT_CLIENT_CERT
    client_key:
        description:
            - "path to an unencrypted PEM-encoded private key matching the client certificate"
        default: to environment variable VAULT_CLIENT_KEY
    verify:
        description:
            - "if set, do not verify presented TLS certificate before communicating with Vault server : setting this variable is not recommended except during testing"
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
    keys:
        description:
            - vault key shard(s).
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_unseal:
      keys: '{{vault_keys}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['keys'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_unseal(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_unseal(params):
    keys = params.get('keys')
    client = hashivault_client(params)
    return {'status': client.unseal_multi(keys.split()), 'changed': True}


if __name__ == '__main__':
    main()
