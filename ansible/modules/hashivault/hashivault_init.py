#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_init
version_added: "2.2.0"
short_description: Hashicorp Vault init enable module
description:
    - Module to init Hashicorp Vault.
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
    pgp_keys:
        description:
            - specifies an array of PGP public keys used to encrypt the output unseal keys.
        default: []
    root_token_pgp_key:
        description:
            - specifies a PGP public key used to encrypt the initial root token.
        default: None
    stored_shares:
        description:
            - specifies the number of shares that should be encrypted.
        default: None
    recovery_shares:
        description:
            - specifies the number of shares to split the recovery key into.
        default: None
    recovery_threshold:
        description:
            - specifies the number of shares required to reconstruct the recovery key.
        default: None
    recovery_pgp_keys:
        description:
            - specifies an array of PGP public keys used to encrypt the output recovery keys.
        default: None
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_init:

- hosts: localhost
  tasks:
    - hashivault_init:
        secret_shares: 7
        secret_threshold: 4
'''


def main():
    argspec = hashivault_argspec()
    argspec['secret_shares'] = dict(required=False, type='int', default=5)
    argspec['secret_threshold'] = dict(required=False, type='int', default=3)
    argspec['pgp_keys'] = dict(required=False, type='list', default=None)
    argspec['root_token_pgp_key'] = dict(required=False, type='str', default=None)
    argspec['stored_shares'] = dict(required=False, type='int', default=None)
    argspec['recovery_shares'] = dict(required=False, type='int', default=None)
    argspec['recovery_threshold'] = dict(required=False, type='int', default=None)
    argspec['recovery_pgp_keys'] = dict(required=False, type='list', default=None)
    module = hashivault_init(argspec)
    result = hashivault_initialize(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_initialize(params):
    client = hashivault_client(params)
    if client.sys.is_initialized():
        return {'changed': False}
    result = {'changed': True}
    secret_shares = params.get('secret_shares')
    secret_threshold = params.get('secret_threshold')
    pgp_keys = params.get('pgp_keys')
    root_token_pgp_key = params.get('root_token_pgp_key')
    stored_shares = params.get('stored_shares')
    recovery_shares = params.get('recovery_shares')
    recovery_threshold = params.get('recovery_threshold')
    recovery_pgp_keys = params.get('recovery_pgp_keys')
    result.update(
        client.sys.initialize(
            secret_shares=secret_shares,
            secret_threshold=secret_threshold,
            pgp_keys=pgp_keys,
            root_token_pgp_key=root_token_pgp_key,
            stored_shares=stored_shares,
            recovery_shares=recovery_shares,
            recovery_threshold=recovery_threshold,
            recovery_pgp_keys=recovery_pgp_keys,
        )
    )
    return result


if __name__ == '__main__':
    main()
