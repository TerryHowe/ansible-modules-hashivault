#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_rekey
version_added: "3.3.0"
short_description: Hashicorp Vault rekey module
description:
    - Module to (update) rekey Hashicorp Vault. Requires that a rekey
      be started with hashivault_rekey_init.
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
            - "path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate : if ca_cert
             is specified, its value will take precedence"
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
            - "if set, do not verify presented TLS certificate before communicating with Vault server : setting this
             variable is not recommended except during testing"
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
        default: to environment variable VAULT_USER
    password:
        description:
            - password to login to vault.
        default: to environment variable VAULT_PASSWORD
    key:
        description:
            - vault key shard (aka unseal key).
    nonce:
        description:
            - rekey nonce.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_rekey:
      key: '{{vault_key}}'
      nonce: '{{nonce}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['key'] = dict(required=True, type='str')
    argspec['nonce'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_rekey(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_rekey(params):
    key = params.get('key')
    nonce = params.get('nonce')
    client = hashivault_client(params)
    return {'status': client.sys.rekey(key, nonce), 'changed': True}


if __name__ == '__main__':
    main()
