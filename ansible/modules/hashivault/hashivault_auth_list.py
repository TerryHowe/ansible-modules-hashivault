#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_auth_list
version_added: "2.2.0"
short_description: Hashicorp Vault auth list module
description:
    - Module to list authentication backends in Hashicorp Vault.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_list:
      register: 'hashivault_auth_list'
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_auth_list(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_auth_list(params):
    client = hashivault_auth_client(params)
    result = client.sys.list_auth_methods()
    if isinstance(result, dict):
        result = result.get('data', result)
    return {'changed': False, 'backends': result}


if __name__ == '__main__':
    main()
