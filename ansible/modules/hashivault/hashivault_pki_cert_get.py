#!/usr/bin/env python
from ansible.module_utils.hashivault import check_secrets_engines
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_cert_get
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Read Certificate
description:
    - This module retrieves one of a selection of certificates.
options:
    serial:
        recuired: true
        defaul: ca
        choices: ["ca", "ca_chain", "crl", "<serial>"]
        description:
            - Specifies the serial of the key to read.
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
    - hashivault_pki_cert_get:
      register: cert
    - debug: msg="{{ cert }}"

    - hashivault_pki_cert_get:
        serial: 0f-d0-bf-cc-7a-d2-b5-b8-ec-6d-8f-cb-9d-0a-c7-d1-e2-3b-82-7d
      register: cert
    - debug: msg="{{ cert }}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['serial'] = dict(required=False, type='str', default='ca')
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    module = hashivault_init(argspec)
    result = hashivault_pki_cert_get(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_cert_get(module):
    params = module.params
    client = hashivault_auth_client(params)

    serial = params.get('serial')
    mount_point = params.get('mount_point').strip('/')

    # check if engine is enabled
    _, err = check_secrets_engines(module, client)
    if err:
        return err

    try:
        return {'data': client.secrets.pki.read_certificate(serial=serial, mount_point=mount_point).get('data')}
    except Exception:
        return {'data': {}}


if __name__ == '__main__':
    main()
