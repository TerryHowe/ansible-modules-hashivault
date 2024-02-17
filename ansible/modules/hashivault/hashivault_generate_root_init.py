#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_generate_root_init
version_added: "3.14.0"
short_description: Hashicorp Vault generate root token init module
description:
    - Module to start root token generation of Hashicorp Vault.
options:
    secret_shares:
        description:
            - specifies the number of shares to split the master key into.
        default: 5
    secret_threshold:
        description:
            - specifies the number of shares required to reconstruct the master key.
        default: 3
    pgp_key:
        description:
            - specifies PGP public keys used to encrypt the output root token.
        default: None
    otp:
        description:
            - must specify either pgp_key or otp
        default: None
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_generate_root_init:
        pgp_key: key
'''


def main():
    argspec = hashivault_argspec()
    argspec['pgp_key'] = dict(required=False, type='str', default=None)
    argspec['otp'] = dict(required=False, type='str', default=None)
    module = hashivault_init(argspec)
    result = hashivault_generate_root_init(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_generate_root_init(params):
    client = hashivault_client(params)
    # Check if rekey is on-going
    status = client.sys.read_root_generation_progress()
    if status['started']:
        return {'changed': False}
    pgp_key = params.get('pgp_key')
    otp = params.get('otp')
    return {'status': client.sys.start_root_token_generation(otp=otp, pgp_key=pgp_key), 'changed': True}


if __name__ == '__main__':
    main()
