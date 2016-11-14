#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_mount_secret_backend
version_added: "2.7.0"
short_description: Hashicorp Vault auth enable module
description:
    - Module to enable authentication backends in Hashicorp Vault.
options:
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    verify:
        description:
            - verify TLS certificate
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
        default: False
    password:
        description:
            - password to login to vault.
        default: False
    backend_type:
        description:
            - type of backend to mount
        default: False
    path:
        description:
            - path to mount
        default: False
    description:
        description:
            - description of path
        default: False
    max_lease_ttl:
        description:
            - max_lease_ttl for the mount
        default: False
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_mount_secret_backend:
        name: "userpass"
'''


def main():
    argspec = hashivault_argspec()
    argspec['backend_type'] = dict(required=True, type='str')
    argspec['path'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    argspec['max_lease_ttl'] = dict(required=False, type='str')
    module = hashivault_init(argspec)
    result = hashivault_mount_secret_backend(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_mount_secret_backend(params):
    client = hashivault_auth_client(params)

    backend_type = params.get('backend_type')
    path = params.get('path')
    description = params.get('description')
    max_lease_ttl = params.get('max_lease_ttl')

    try:
        client.enable_secret_backend(backend_type,
                                     description=description,
                                     mount_point=path,
                                     config={'max_lease_ttl': max_lease_ttl})
    except Exception, e:
        if "existing mount at {path}".format(path=path) in e.message:
            params = {
            'max_lease_ttle': max_lease_ttl
            }

            result = client._post('/v1/sys/mounts/{path}/tune'.format(path=path), json=params)
            return {'changed': True}
        else:
            raise e

    return {'changed': True}


if __name__ == '__main__':
    main()