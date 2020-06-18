#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role_list
version_added: "3.8.0"
short_description: Hashicorp Vault approle list roles module
description:
    - Module to list approle roles from Hashicorp Vault.
options:
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
    - hashivault_approle_role_list:
      register: 'vault_approle_role_list'
    - debug: msg="Roles are {{vault_approle_role_list.roles}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='approle')
    module = hashivault_init(argspec)
    result = hashivault_approle_role_list(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role_list(params):
    client = hashivault_auth_client(params)
    roles = client.list_roles(mount_point=params.get('mount_point'))
    roles = roles.get('data', {}).get('keys', [])
    return {'roles': roles}


if __name__ == '__main__':
    main()
