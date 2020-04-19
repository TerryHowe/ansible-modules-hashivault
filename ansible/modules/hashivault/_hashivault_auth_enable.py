#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['deprecated'], 'alternative': 'Use M(hashivault_auth_method) instead.',
                    'why': 'This module does not fit the standard pattern',
                    'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_auth_enable
version_added: "2.2.0"
short_description: Hashicorp Vault auth enable module
description:
    - Use hashivault_auth_method instead.
options:
    name:
        description:
            - name of authenticator
    description:
        description:
            - description of authenticator
    mount_point:
        description:
            - location where this auth backend will be mounted
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_enable:
        name: "userpass"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default=None)
    module = hashivault_init(argspec)
    result = hashivault_auth_enable(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_auth_enable(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    description = params.get('description')
    mount_point = params.get('mount_point')
    result = client.sys.list_auth_methods()
    backends = result.get('data', result)
    path = (mount_point or name) + u"/"
    if path in backends:
        return {'changed': False}
    client.sys.enable_auth_method(name, description=description, path=mount_point)
    return {'changed': True}


if __name__ == '__main__':
    main()
