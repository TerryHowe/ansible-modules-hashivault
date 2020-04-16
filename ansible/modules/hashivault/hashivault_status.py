#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_status
version_added: "1.2.0"
short_description: Hashicorp Vault status module
description:
    - Module to get status of Hashicorp Vault.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_status:
      register: 'vault_status'
    - debug: msg="Seal progress is {{vault_status.status.progress}}"
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_status(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_status(params):
    client = hashivault_client(params)
    return {'status': client.sys.read_seal_status()}


if __name__ == '__main__':
    main()
