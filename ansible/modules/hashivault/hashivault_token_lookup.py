#!/usr/bin/env python

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_token_lookup
version_added: "3.3.0"
short_description: Hashicorp Vault token lookup module
description:
    - Module to look up / check for existence of tokens in Hashicorp Vault.
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
    lookup_token:
        description:
            - token to lookup if different from auth token
        default: to authentication token
    accessor:
        description:
            - If set, lookups will use the this accessor token
    wrap_ttl:
        description:
            - Indicates that the response should be wrapped in a cubbyhole token with the requested TTL.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - name: "Lookup token"
      hashivault_token_lookup:
        lookup_token: "{{client_token}}"
      register: "vault_token_lookup"
'''


def main():
    argspec = hashivault_argspec()
    argspec['lookup_token'] = dict(required=False, type='str')
    argspec['accessor'] = dict(required=False, type='bool', default=False)
    argspec['wrap_ttl'] = dict(required=False, type='int')
    module = hashivault_init(argspec)
    result = hashivault_token_lookup(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_token_lookup(params):
    client = hashivault_auth_client(params)
    accessor = params.get('accessor')
    lookup_token = params.get('lookup_token')
    if lookup_token is None:
        lookup_token = params.get('token')
    wrap_ttl = params.get('wrap_ttl')
    lookup = client.lookup_token(token=lookup_token, accessor=accessor, wrap_ttl=wrap_ttl)
    return {'changed': False, 'lookup': lookup}


if __name__ == '__main__':
    main()
