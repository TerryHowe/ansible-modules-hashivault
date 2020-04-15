#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['deprecated'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_userpass_create
version_added: "2.2.0"
short_description: Hashicorp Vault userpass create module
description:
    - Module to create userpass users in Hashicorp Vault. Use hashicorp_userpass instead.
options:
    name:
        description:
            - user name to create.
    pass:
        description:
            - user to create password.
    policies:
        description:
            - user policies.
        default: default
    mount_point:
        description:
            - default The "path" (app-id) the auth backend is mounted on.
        default: userpass
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_userpass_create:
      name: 'bob'
      pass: 'S3cre7s'
      policies: 'bob'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['pass'] = dict(required=True, type='str')
    argspec['policies'] = dict(required=False, type='str', default='default')
    argspec['mount_point'] = dict(required=False, type='str', default='userpass', no_log=True)
    module = hashivault_init(argspec)
    result = hashivault_userpass_create(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_userpass_create(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    password = params.get('pass')
    policies = params.get('policies')
    mount_point = params.get('mount_point')
    client.create_userpass(name, password, policies, mount_point=mount_point)
    return {'changed': True}


if __name__ == '__main__':
    main()
