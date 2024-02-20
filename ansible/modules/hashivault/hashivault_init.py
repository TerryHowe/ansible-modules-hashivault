#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_init
version_added: "2.2.0"
short_description: Hashicorp Vault init enable module
description:
    - Module to init Hashicorp Vault.
options:
    seal_method:
        description:
            - specifies if `secret_*` or `recovery_*` options should be used.
        default: secret
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
    root_token_pgp_key:
        description:
            - specifies a PGP public key used to encrypt the initial root token.
        default: None
    stored_shares:
        description:
            - specifies the number of shares that should be encrypted.
        default: None
    recovery_shares:
        description:
            - specifies the number of shares to split the recovery key into.
        default: 5
    recovery_threshold:
        description:
            - specifies the number of shares required to reconstruct the recovery key.
        default: 3
    recovery_pgp_keys:
        description:
            - specifies an array of PGP public keys used to encrypt the output recovery keys.
        default: None
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_init:

- hosts: localhost
  tasks:
    - hashivault_init:
        secret_shares: 7
        secret_threshold: 4
'''


def main():
    argspec = hashivault_argspec()
    argspec['seal_method'] = dict(
        required=False, type='str', default='secret', choices=['secret', 'recovery']
    )
    argspec['secret_shares'] = dict(required=False, type='int', default=None)
    argspec['secret_threshold'] = dict(required=False, type='int', default=None)
    argspec['pgp_keys'] = dict(required=False, type='list', default=None)
    argspec['root_token_pgp_key'] = dict(required=False, type='str', default=None)
    argspec['stored_shares'] = dict(required=False, type='int', default=None)
    argspec['recovery_shares'] = dict(required=False, type='int', default=None)
    argspec['recovery_threshold'] = dict(required=False, type='int', default=None)
    argspec['recovery_pgp_keys'] = dict(required=False, type='list', default=None)
    module = hashivault_init(argspec)
    additional_parameter_handling(module)
    result = hashivault_initialize(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def additional_parameter_handling(module):
    '''Additional parameter validation'''

    # Default shares and thresholds depending on the seal method
    if module.params.get('seal_method') == 'secret':
        module.params['secret_shares'] = (
            5
            if module.params.get('secret_shares') is None
            else module.params.get('secret_shares')
        )
        module.params['secret_threshold'] = (
            3
            if module.params.get('secret_threshold') is None
            else module.params.get('secret_threshold')
        )

        if (
            module.params.get('recovery_shares')
            or module.params.get('recovery_threshold')
            or module.params.get('recovery_pgp_keys')
        ):
            module.fail_json(
                msg="'recovery_*' options are only valid if 'seal_method' == 'recovery'",
                changed=False,
            )
    else:
        module.params['recovery_shares'] = (
            5
            if module.params.get('recovery_shares') is None
            else module.params.get('recovery_shares')
        )
        module.params['recovery_threshold'] = (
            3
            if module.params.get('recovery_threshold') is None
            else module.params.get('recovery_threshold')
        )

        if module.params.get('secret_shares') or module.params.get('secret_threshold'):
            module.fail_json(
                msg="'secret_*' options are only valid if 'seal_method' == 'secret'",
                changed=False,
            )


@hashiwrapper
def hashivault_initialize(params):
    client = hashivault_client(params)
    if client.sys.is_initialized():
        return {'changed': False}
    result = {'changed': True}
    secret_shares = params.get('secret_shares')
    secret_threshold = params.get('secret_threshold')
    pgp_keys = params.get('pgp_keys')
    root_token_pgp_key = params.get('root_token_pgp_key')
    stored_shares = params.get('stored_shares')
    recovery_shares = params.get('recovery_shares')
    recovery_threshold = params.get('recovery_threshold')
    recovery_pgp_keys = params.get('recovery_pgp_keys')
    result.update(
        client.sys.initialize(
            secret_shares=secret_shares,
            secret_threshold=secret_threshold,
            pgp_keys=pgp_keys,
            root_token_pgp_key=root_token_pgp_key,
            stored_shares=stored_shares,
            recovery_shares=recovery_shares,
            recovery_threshold=recovery_threshold,
            recovery_pgp_keys=recovery_pgp_keys,
        )
    )
    return result


if __name__ == '__main__':
    main()
