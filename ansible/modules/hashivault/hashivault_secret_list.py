#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_secret_list
version_added: "2.2.0"
short_description: Hashicorp Vault secret list module
description:
    - Module to list secret backends in Hashicorp Vault.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_secret_list:
      register: 'hashivault_secret_list'
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_secret_list(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_secret_list(params):
    client = hashivault_auth_client(params)
    current_backends = client.sys.list_mounted_secrets_engines()
    if isinstance(current_backends, dict):
        current_backends = current_backends.get('data', current_backends)
    return {'changed': False, 'backends': current_backends}


if __name__ == '__main__':
    main()
