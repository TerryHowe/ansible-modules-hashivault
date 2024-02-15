#!/usr/bin/env python

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role_secret_get
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
    secret:
        description:
            - secret id.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_approle_role_secret_get:
        name: 'ashley'
        secret: 'ec4bedee-e44b-c096-9ac8-1600e52ed8f8'
      register: 'vault_approle_role_secret_get'
    - debug: msg="Role secret is {{vault_approle_role_secret_get.secret}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='approle')
    argspec['secret'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_approle_role_secret_get(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role_secret_get(params):
    try:
        name = params.get('name')
        mount_point = params.get('mount_point')
        secret = params.get('secret')
        client = hashivault_auth_client(params)
        response = client.auth.approle.read_secret_id(name, secret, mount_point=mount_point)
        if type(response) is not dict and response.status_code == 204:  # No content
            return {'secret': {}, 'status': 'absent'}
        else:
            return {'secret': response['data'], 'response': response, 'status': 'present'}
    except Exception as e:
        return {'failed': True, 'msg': str(e)}


if __name__ == '__main__':
    main()
