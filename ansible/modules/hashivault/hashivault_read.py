#!/usr/bin/env python

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashivault_read

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_read
version_added: "0.1"
short_description: Hashicorp Vault read module
description:
    - Module to read to Hashicorp Vault.
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
            - "authentication type to use: token, userpass, github, ldap, approle"
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
    version:
        description:
            - version of the kv engine (int)
        default: 1
    mount_point:
        description:
            - secret mount point
        default: secret
    secret:
        description:
            - secret to read.
    key:
        description:
            - secret key to read.
    register:
        description:
            - variable to register result.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_read:
        secret: 'giant'
        key: 'fie'
      register: 'fie'
    - debug: msg="Value is {{fie.value}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['version'] = dict(required=False, type='int', default=1)
    argspec['mount_point'] = dict(required=False, type='str', default='secret')
    argspec['secret'] = dict(required=True, type='str')
    argspec['key'] = dict(required=False, type='str')
    argspec['register'] = dict(required=False, type='str')
    argspec['default'] = dict(required=False, default=None, type='str')
    module = hashivault_init(argspec)
    result = hashivault_read(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


if __name__ == '__main__':
    main()
