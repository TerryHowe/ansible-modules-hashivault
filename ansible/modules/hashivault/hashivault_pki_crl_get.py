#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_crl_get
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Read CRL Configuration
description:
    - This module allows getting the duration for which the generated CRL should be marked valid.
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
    - hashivault_pki_crl_get:
      register: clr_config
    - debug: msg="{{ clr_config }}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    module = hashivault_init(argspec)
    result = hashivault_pki_crl_get(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_crl_get(module):
    params = module.params
    client = hashivault_auth_client(params)

    mount_point = params.get('mount_point').strip('/')

    result = {"changed": False, "rc": 0}
    from hvac.exceptions import InvalidPath
    try:
        result['data'] = client.secrets.pki.read_crl_configuration(mount_point=mount_point).get('data')
    except InvalidPath:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"CRLs must be configured before reading"
    except Exception as e:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Exception: " + str(e)
    return result


if __name__ == '__main__':
    main()
