#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_audit_list
version_added: "2.2.0"
short_description: Hashicorp Vault audit list module
description:
    - Module to list audit backends in Hashicorp Vault.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_audit_list:
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_audit_list(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_audit_list(params):
    client = hashivault_auth_client(params)
    backends = client.sys.list_enabled_audit_devices()
    backends = backends.get('data', backends)
    return {'changed': False, 'backends': backends}


if __name__ == '__main__':
    main()
