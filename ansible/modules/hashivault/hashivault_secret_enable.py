#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_secret_enable
version_added: "2.2.0"
short_description: Hashicorp Vault secret enable module
description:
    - Module to enable secret backends in Hashicorp Vault.
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
            - name of secret backend
    backend:
        description:
            - type of secret backend
    description:
        description:
            - description of secret backend
    config:
        description:
            - config of secret backend
    options:
        description:
            - options of secret backend
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_secret_enable:
        name: "ephemeral"
        backend: "generic"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['backend'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    argspec['config'] = dict(required=False, type='dict')
    argspec['options'] = dict(required=False, type='dict')
    module = hashivault_init(argspec)
    result = hashivault_secret_enable(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_secret_enable(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    backend = params.get('backend')
    description = params.get('description')
    config = params.get('config')
    options = params.get('options')
    secrets = client.sys.list_mounted_secrets_engines()
    secrets = secrets.get('data', secrets)
    path = name + "/"
    if path in secrets:
        return {'changed': False}
    client.sys.enable_secrets_engine(backend, description=description, path=name, config=config, options=options)
    return {'changed': True}


if __name__ == '__main__':
    main()
