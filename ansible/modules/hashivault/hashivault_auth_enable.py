#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_auth_enable
version_added: "2.2.0"
short_description: Hashicorp Vault auth enable module
description:
    - Module to enable authentication backends in Hashicorp Vault.
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
    name:
        description:
            - name of authenticator
    description:
        description:
            - description of authenticator
    mount_point
        description:
            - location where this auth backend will be mounted 
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_enable:
        name: "userpass"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default=None)
    module = hashivault_init(argspec)
    result = hashivault_auth_enable(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_auth_enable(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    description = params.get('description')
    mount_point = params.get('mount_point')
    backends = client.list_auth_backends()
    path = (mount_point or name) + "/"
    if path in backends:
        return {'changed': False}
    client.enable_auth_backend(name, description=description, mount_point=mount_point)
    return {'changed': True}


if __name__ == '__main__':
    main()
