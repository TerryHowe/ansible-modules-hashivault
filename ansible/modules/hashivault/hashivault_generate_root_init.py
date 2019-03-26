#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_generate_root_init
version_added: "3.14.0"
short_description: Hashicorp Vault generate root token init module
description:
    - Module to start root token generation of Hashicorp Vault.
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
    secret_shares:
        description:
            - specifies the number of shares to split the master key into.
        default: 5
    secret_threshold:
        description:
            - specifies the number of shares required to reconstruct the master key.
        default: 3
    pgp_key:
        description:
            - specifies PGP public keys used to encrypt the output root token.
        default: ''
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_generate_root_init:
        pgp_key: key
'''


def main():
    argspec = hashivault_argspec()
    argspec['pgp_key'] = dict(required=False, type='str', default='')
    module = hashivault_init(argspec)
    result = hashivault_generate_root_init(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_generate_root_init(params):
    client = hashivault_client(params)
    # Check if rekey is on-going
    status = client.generate_root_status
    if status['started']:
        return {'changed': False}
    pgp = params.get('pgp_key')
    return {'status': client.start_generate_root(pgp, otp=False), 'changed': True}


if __name__ == '__main__':
    main()
