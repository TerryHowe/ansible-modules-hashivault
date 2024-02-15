#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
from ansible.module_utils.hashivault import hashivault_client

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_generate_root
version_added: "3.14.0"
short_description: Hashicorp Vault generate_root module
description:
    - Module to (update) generate_root Hashicorp Vault.
options:
    key:
        description:
            - vault key shard.
    nonce:
        description:
            - generate_root nonce.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_generate_root:
      key: '{{vault_unseal_key}}'
      nonce: '{{nonce}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['key'] = dict(required=False, type='str', no_log=True)
    argspec['nonce'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_generate_root(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_generate_root(params):
    key = params.get('key')
    nonce = params.get('nonce')
    client = hashivault_client(params)
    return {'status': client.sys.generate_root(key, nonce), 'changed': True}


if __name__ == '__main__':
    main()
