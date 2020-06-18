#!/usr/bin/env python
from ansible.module_utils.hashivault import check_secrets_engines
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import compare_state
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_url
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Set URLs
description:
    - This module allows setting the issuing certificate endpoints, CRL distribution points, and OCSP server endpoints
      that will be encoded into issued certificates.
    - You can update any of the values at any time without affecting the other existing values.
    - To remove the values, simply use a blank string as the parameter.
options:
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
    issuing_certificates:
        type: list
        description:
            - Specifies the URL values for the Issuing Certificate field.
    crl_distribution_points:
        type: list
        description:
            -  Specifies the URL values for the CRL Distribution Points field.
    ocsp_servers:
        type: list
        description:
            -  Specifies the URL values for the OCSP Servers field.
extends_documentation_fragment:
    - hashivault
'''

EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - hashivault_pki_url:
        issuing_certificates:
            - 'http://127.0.0.1:8200/v1/pki/ca'
        crl_distribution_points:
            - 'http://127.0.0.1:8200/v1/pki/crl'

'''


def main():
    argspec = hashivault_argspec()
    argspec['issuing_certificates'] = dict(required=False, type='list', default=[])
    argspec['crl_distribution_points'] = dict(required=False, type='list', default=[])
    argspec['ocsp_servers'] = dict(required=False, type='list', default=[])
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_pki_url(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_url(module):
    params = module.params
    client = hashivault_auth_client(params)

    mount_point = params.get('mount_point').strip('/')

    desired_state = {
        'issuing_certificates': params.get('issuing_certificates'),
        'crl_distribution_points': params.get('crl_distribution_points'),
        'ocsp_servers': params.get('ocsp_servers')
    }

    # check if engine is enabled
    changed, err = check_secrets_engines(module, client)
    if err:
        return err

    # check if config exists
    current_state = {}
    try:
        current_state = client.secrets.pki.read_urls(mount_point=mount_point).get('data')
    except Exception:
        # not configured yet.
        changed = True

    # compare current_state to desired_state
    if not changed:
        changed = not compare_state(desired_state, current_state)

    # make the changes!
    if changed and not module.check_mode:
        client.secrets.pki.set_urls(mount_point=mount_point, params=desired_state)
    return {'changed': changed}


if __name__ == '__main__':
    main()
