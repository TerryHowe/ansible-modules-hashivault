#!/usr/bin/env python

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['deprecated'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role_secret_delete
version_added: "3.8.0"
short_description: Hashicorp Vault approle role secret id delete module
description:
    - Module to delete a approle role secret id from Hashicorp Vault. Use hashivault_approle_role_secret instead.
options:
    name:
        description:
            - role name.
    secret:
        description:
            - secret id.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_approle_role_secret_delete:
        name: 'ashley'
        secret: 'ec4bedee-e44b-c096-9ac8-1600e52ed8f8'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['secret'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_approle_role_secret_delete(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role_secret_delete(params):
    name = params.get('name')
    secret = params.get('secret')
    client = hashivault_auth_client(params)
    client.delete_role_secret_id(name, secret)
    return {'changed': True}


if __name__ == '__main__':
    main()
