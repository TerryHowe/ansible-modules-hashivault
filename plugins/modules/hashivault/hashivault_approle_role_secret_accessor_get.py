#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role_secret_accessor_get
version_added: "3.8.0"
short_description: Hashicorp Vault approle role secret accessor get module
description:
    - Module to get a approle role secret accessor from Hashicorp Vault.
options:
    name:
        description:
            - role name.
    mount_point:
        description:
            - mount point for role
        default: approle
    accessor:
        description:
            - accessor id.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_approle_role_secret_accessor_get:
        name: 'ashley'
        accessor: 'ec4bedee-e44b-c096-9ac8-1600e52ed8f8'
      register: 'vault_approle_role_secret_accessor_get'
    - debug: msg="Role secret is {{vault_approle_role_secret_accessor_get.secret}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='approle')
    argspec['accessor'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_approle_role_secret_accessor_get(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role_secret_accessor_get(params):
    name = params.get('name')
    mount_point = params.get('mount_point')
    accessor = params.get('accessor')
    client = hashivault_auth_client(params)
    return {'secret': client.get_role_secret_id_accessor(name, accessor, mount_point=mount_point)['data']}


if __name__ == '__main__':
    main()
