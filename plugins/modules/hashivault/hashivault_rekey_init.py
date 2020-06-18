#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_rekey_init
version_added: "3.3.0"
short_description: Hashicorp Vault rekey init module
description:
    - Module to start rekey Hashicorp Vault.
options:
    secret_shares:
        description:
            - specifies the number of shares to split the master key into.
        default: 5
    secret_threshold:
        description:
            - specifies the number of shares required to reconstruct the master key.
        default: 3
    pgp_keys:
        description:
            - specifies an array of PGP public keys used to encrypt the output unseal keys.
        default: []
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_rekey_init:
        secret_shares: 7
        secret_threshold: 4
'''


def main():
    argspec = hashivault_argspec()
    argspec['secret_shares'] = dict(required=False, type='int', default=5)
    argspec['secret_threshold'] = dict(required=False, type='int', default=3)
    argspec['pgp_keys'] = dict(required=False, type='list', default=[], no_log=True)
    argspec['backup'] = dict(required=False, type='bool', default=False)
    module = hashivault_init(argspec)
    result = hashivault_rekey_init(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_rekey_init(params):
    client = hashivault_client(params)
    # Check if rekey is on-going, exit if there is a rekey in progress
    status = client.rekey_status
    if status['started']:
        return {'changed': False}
    secret_shares = params.get('secret_shares')
    secret_threshold = params.get('secret_threshold')
    pgp_keys = params.get('pgp_keys')
    backup = params.get('backup')
    return {'status': client.sys.start_rekey(secret_shares, secret_threshold, pgp_keys, backup), 'changed': True}


if __name__ == '__main__':
    main()
