#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role_id
version_added: "3.8.0"
short_description: Hashicorp Vault approle get role id module
description:
    - Module to get a approle role id from Hashicorp Vault.
options:
    name:
        description:
            - role name.
    mount_point:
        description:
            - mount point for role
        default: approle
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_approle_role_id:
        name: 'ashley'
      register: 'vault_approle_role_id'
    - debug: msg="Role id is {{vault_approle_role_id.id}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='approle')
    module = hashivault_init(argspec)
    result = hashivault_approle_role_id(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role_id(params):
    name = params.get('name')
    client = hashivault_auth_client(params)
    result = client.auth.approle.read_role_id(name, mount_point=params.get('mount_point'))
    data = result.get('data', {})
    role_id = data.get('role_id', '')
    return {'id': role_id, 'data': data}


if __name__ == '__main__':
    main()
