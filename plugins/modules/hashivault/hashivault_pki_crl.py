#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import is_state_changed
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_crl
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Set CRL Configuration
description:
    - This module allows setting the duration for which the generated CRL should be marked valid.
    - If the CRL is disabled, it will return a signed but zero-length CRL for any request.
    - If enabled, it will re-build the CRL.
options:
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
    expiry:
        required: true
        type: str
        description:
            - Specifies the time until expiration.
    disable:
        type: bool
        default: false
        description:
            - Disables or enables CRL building.
extends_documentation_fragment:
    - hashivault
'''
EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - hashivault_pki_crl:
        expiry: 72h
        disable: false

'''


def main():
    argspec = hashivault_argspec()
    argspec['expiry'] = dict(required=True, type='str')
    argspec['disable'] = dict(required=False, type='bool', default=False)
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_pki_crl(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_crl(module):
    params = module.params
    client = hashivault_auth_client(params)

    mount_point = params.get('mount_point').strip('/')

    desired_state = {
        'disable': params.get('disable'),
        'expiry': params.get('expiry')
    }

    # compare current_state to desired_state
    from hvac.exceptions import InvalidPath
    try:
        current_state = client.secrets.pki.read_crl_configuration(mount_point=mount_point).get('data')
        changed = is_state_changed(desired_state, current_state)
    except InvalidPath:
        changed = True

    # make the changes!
    if changed and not module.check_mode:
        client.secrets.pki.set_crl_configuration(mount_point=mount_point, extra_params=desired_state)
    return {'changed': changed}


if __name__ == '__main__':
    main()
