#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_generate_root_cancel
version_added: "3.14.0"
short_description: Hashicorp Vault generate_root cancel module
description:
    - Module to cancel generation of root token of Hashicorp Vault.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_generate_root_cancel:
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_generate_root_cancel(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_generate_root_cancel(params):
    client = hashivault_client(params)
    # Check if generate_root is on-going & return when generate_root not in progress
    status = client.sys.read_root_generation_progress()
    if not status['started']:
        return {'changed': False}
    return {'status': client.sys.cancel_root_generation().ok, 'getter': str(status), 'changed': True}


if __name__ == '__main__':
    main()
