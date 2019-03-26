#!/usr/bin/env python

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role_secret_create
version_added: "3.8.0"
short_description: Hashicorp Vault approle role secret id get module
description:
    - Module to get a approle role secret id from Hashicorp Vault.
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
    name:
        description:
            - secret name.
    cidr_list:
        description:
            - Comma-separated string or list of CIDR blocks.
    metadata:
        description:
            - Metadata to be tied to the secret.
    wrap_ttl:
        description:
            - Wrap TTL.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_approle_role_secret_create:
        name: 'ashley'
      register: 'vault_approle_role_secret_create'
    - debug: msg="Role secret id is {{vault_approle_role_secret_create.id}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['cidr_list'] = dict(required=False, type='str')
    argspec['metadata'] = dict(required=False, type='dict')
    argspec['wrap_ttl'] = dict(required=False, type='str')
    module = hashivault_init(argspec)
    result = hashivault_approle_role_secret_create(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role_secret_create(params):
    name = params.get('name')
    cidr_list = params.get('cidr_list')
    metadata = params.get('metadata')
    wrap_ttl = params.get('wrap_ttl')
    kwargs = {}
    if cidr_list is not None:
        kwargs['cidr_list'] = cidr_list
    if metadata is not None:
        kwargs['meta'] = metadata
    if wrap_ttl is not None:
        kwargs['wrap_ttl'] = wrap_ttl
    client = hashivault_auth_client(params)
    result = client.create_role_secret_id(name, **kwargs)
    return result['data']


if __name__ == '__main__':
    main()
