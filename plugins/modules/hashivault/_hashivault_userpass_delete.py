#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['deprecated'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_userpass_delete
version_added: "2.2.0"
short_description: Hashicorp Vault userpass delete module
description:
    - Module to delete userpass users in Hashicorp Vault. Use hashicorp_userpass instead.
options:
    name:
        description:
            - user name.
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
    - hashivault_userpass_delete:
      name: 'bob'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='userpass')
    module = hashivault_init(argspec)
    result = hashivault_userpass_delete(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_userpass_delete(params):
    client = hashivault_auth_client(params)
    username = params.get('name')
    mount_point = params.get('mount_point')
    client.delete_userpass(username, mount_point=mount_point)
    return {'changed': True}


if __name__ == '__main__':
    main()
