#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_rekey
version_added: "3.3.0"
short_description: Hashicorp Vault rekey module
description:
    - Module to (update) rekey Hashicorp Vault. Requires that a rekey
      be started with hashivault_rekey_init.
options:
    key:
        description:
            - vault key shard (aka unseal key).
    nonce:
        description:
            - rekey nonce.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - name: Start a rekey
      hashivault_rekey_init:
        secret_shares: 1
        secret_threshold: 1
        verification_required: True
      register: 'vault_rekey_init'

    - name: Update the rekey
      hashivault_rekey:
        key: "{{ unseal_key }}"
        nonce: "{{ vault_rekey_init.status.nonce }}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['key'] = dict(required=True, type='str', no_log=True)
    argspec['nonce'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_rekey(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_rekey(params):
    key = params.get('key')
    nonce = params.get('nonce')
    client = hashivault_client(params)
    return {'status': client.sys.rekey(key, nonce), 'changed': True}


if __name__ == '__main__':
    main()
