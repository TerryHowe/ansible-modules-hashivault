#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_rekey_cancel
version_added: "3.3.0"
short_description: Hashicorp Vault rekey cancel module
description:
    - Module to cancel rekey Hashicorp Vault.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_rekey_cancel:
      register: "vault_rekey_cancel"
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_rekey_cancel(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_rekey_cancel(params):
    client = hashivault_client(params)
    # Check if rekey is on-going & return when rekey not in progress
    status = client.rekey_status
    if not status['started']:
        return {'changed': False}
    return {'status': client.sys.cancel_rekey().ok, 'changed': True}


if __name__ == '__main__':
    main()
