#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_mount_tune
version_added: "3.7.0"
short_description: Hashicorp Vault tune backend
description:
    - Module to enable tuning of backends in HashiCorp Vault.
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
    mount_point:
        description:
            - location where this auth backend will be mounted
    default_lease_ttl:
        description:
            - Configures the default lease duration for tokens and secrets. This is an integer value in seconds.
    max_lease_ttl:
        description:
            - Configures the maximum lease duration for tokens and secrets. This is an integer value in seconds.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_mount_tune:
        mount_point: ephemeral
        default_lease_ttl: 3600
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=True, type='str')
    argspec['default_lease_ttl'] = dict(required=False, type='int', default=None)
    argspec['max_lease_ttl'] = dict(required=False, type='int', default=None)
    module = hashivault_init(argspec)
    result = hashivault_mount_tune(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_mount_tune(module):
    client = hashivault_auth_client(module.params)
    mount_point = module.params.get('mount_point')
    default_lease_ttl = module.params.get('default_lease_ttl')
    max_lease_ttl = module.params.get('max_lease_ttl')

    changed = False
    current_tuning = client.sys.read_mount_configuration(mount_point)
    current_tuning = current_tuning.get('data', current_tuning)
    current_default_lease_ttl = current_tuning.get('default_lease_ttl')
    current_max_lease_ttl = current_tuning.get('max_lease_ttl')

    if (current_default_lease_ttl != default_lease_ttl) or (current_max_lease_ttl != max_lease_ttl):
        changed = True

    if not module.check_mode:
        client.sys.tune_mount_configuration(mount_point, default_lease_ttl=default_lease_ttl,
                                            max_lease_ttl=max_lease_ttl)

    return {'changed': changed}

if __name__ == '__main__':
    main()
