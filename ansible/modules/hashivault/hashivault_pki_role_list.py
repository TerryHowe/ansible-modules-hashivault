#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_role_list
version_added: "4.5.0"
short_description: Hashicorp Vault PKI List Roles
description:
    - This module returns a list of available roles.
    - Only the role names are returned, not any values.
options:
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
extends_documentation_fragment:
    - hashivault
'''
EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - hashivault_pki_role_list:
        mount_point: pki
      register: roles_list
    - debug: msg="{{ roles_list.data }}"
'''
RETURN = r'''
---
data:
    description: list of roles, if pki engine has no roles will return empty list
    returned: success
    type: list
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    module = hashivault_init(argspec)
    result = hashivault_pki_role_list(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_role_list(module):
    params = module.params
    client = hashivault_auth_client(params)

    mount_point = params.get('mount_point').strip('/')

    try:
        return {'data': client.secrets.pki.list_roles(mount_point=mount_point).get('data').get('keys')}
    except Exception:
        return {'data': []}


if __name__ == '__main__':
    main()
