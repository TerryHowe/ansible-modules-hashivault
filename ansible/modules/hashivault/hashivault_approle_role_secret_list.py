#!/usr/bin/env python
from hvac.exceptions import InvalidPath
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role_secret_list
version_added: "3.8.0"
short_description: Hashicorp Vault approle role secret id get module
description:
    - Module to get a approle role secret id from Hashicorp Vault.
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
    - hashivault_approle_role_secret_list:
        name: 'ashley'
      register: 'vault_approle_role_secret_list'
    - debug: msg="Role secrets are {{vault_approle_role_secret_list.secrets}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='approle')
    module = hashivault_init(argspec)
    result = hashivault_approle_role_secret_list(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role_secret_list(params):
    name = params.get('name')
    mount_point = params.get('mount_point')
    client = hashivault_auth_client(params)
    try:
        secrets = client.auth.approle.list_secret_id_accessors(name, mount_point=mount_point)
    except InvalidPath:
        return {'secrets': []}
    secrets = secrets.get('data', {}).get('keys', [])
    return {'secrets': str(secrets)}


if __name__ == '__main__':
    main()
