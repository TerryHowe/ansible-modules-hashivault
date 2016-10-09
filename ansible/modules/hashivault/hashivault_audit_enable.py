#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_audit_enable
version_added: "2.2.0"
short_description: Hashicorp Vault audit enable module
description:
    - Module to enable audit backends in Hashicorp Vault.
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
    name:
        description:
            - name of auditor
        default: False
    description:
        description:
            - description of auditor
        default: False
    options:
        description:
            - options for auditor
        default: False
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_audit_enable:
        name: "syslog"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    argspec['options'] = dict(required=False, type='dict')
    module = hashivault_init(argspec)
    result = hashivault_audit_enable(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_audit_enable(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    description = params.get('description')
    options = params.get('options')
    client.enable_audit_backend(name, description=description, options=options)
    return {'changed': True}


if __name__ == '__main__':
    main()
