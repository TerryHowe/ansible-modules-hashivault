#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_seal
version_added: "1.2.0"
short_description: Hashicorp Vault seal module
description:
    - Module to seal Hashicorp Vault.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_seal:
      register: 'vault_seal'
    - debug: msg="Seal return is {{vault_seal.rc}}"
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_seal(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_seal(params):
    client = hashivault_auth_client(params)
    if not client.sys.is_sealed():
        status = client.sys.seal().ok
        return {'status': status, 'changed': True}
    else:
        return {'changed': False}


if __name__ == '__main__':
    main()
