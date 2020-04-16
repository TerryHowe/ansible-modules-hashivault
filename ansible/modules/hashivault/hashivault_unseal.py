#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_unseal
version_added: "1.2.0"
short_description: Hashicorp Vault unseal module
description:
    - Module to unseal Hashicorp Vault.
options:
    keys:
        description:
            - vault key shard(s).
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_unseal:
      keys: '{{vault_keys}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['keys'] = dict(required=True, type='str', no_log=True)
    module = hashivault_init(argspec)
    result = hashivault_unseal(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_unseal(params):
    keys = params.get('keys')
    client = hashivault_client(params)
    if client.sys.is_sealed():
        return {'status': client.sys.submit_unseal_keys(keys.split()), 'changed': True}
    else:
        return {'changed': False}


if __name__ == '__main__':
    main()
