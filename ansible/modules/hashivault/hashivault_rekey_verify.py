#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_rekey_verify
version_added: "4.6.2"
short_description: Hashicorp Vault rekey verify module
description:
    - Module to verify a rekey of Hashicorp Vault. Requires that a rekey
      be started with hashivault_rekey_init passing verification_required == True
      and being successfully completed.
options:
    key:
        description:
            - vault key shard (aka unseal key). The new, freshly generated one.
    nonce:
        description:
            - verify nonce.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_rekey_verify:
      key: '{{vault_key}}'
      nonce: '{{nonce}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['key'] = dict(required=True, type='str', no_log=True)
    argspec['nonce'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_rekey_verify(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_rekey_verify(params):
    key = params.get('key')
    nonce = params.get('nonce')
    client = hashivault_client(params)
    return {'status': client.sys.rekey_verify(key, nonce), 'changed': True}


if __name__ == '__main__':
    main()
