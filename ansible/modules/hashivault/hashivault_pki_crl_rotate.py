#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_crl_rotate
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Rotate CRLs
description:
    - This module forces a rotation of the CRL.
    - This can be used by administrators to cut the size of the CRL if it contains a number of certificates that have
      now expired, but has not been rotated due to no further certificates being revoked.
options:
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
extends_documentation_fragment:
    - hashivault
'''
EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - hashivault_pki_crl_rotate:
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_pki_crl_rotate(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_crl_rotate(module):
    params = module.params
    client = hashivault_auth_client(params)

    mount_point = params.get('mount_point').strip('/')

    failed = False

    # make the changes!
    if not module.check_mode:
        failed = not client.secrets.pki.rotate_crl(mount_point=mount_point).get('data').get('success')
    return {'failed': failed, 'changed': not failed,
            'msg': 'oops, something went wrong.' if failed else '', 'rc': 1 if failed else 0}


if __name__ == '__main__':
    main()
