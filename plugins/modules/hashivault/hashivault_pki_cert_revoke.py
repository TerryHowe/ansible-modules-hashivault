#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_cert_revoke
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Revoke Certificate
description:
    - This module revokes a certificate using its serial number.
    - This is an alternative option to the standard method of revoking using Vault lease IDs.
    - A successful revocation will rotate the CRL.
options:
    serial:
        recuired: true
        description:
            - Specifies the serial number of the certificate to revoke, in hyphen-separated or colon-separated octal.
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
    - hashivault_pki_cert_revoke:
        role: 'tester'
        common_name: 'test.example.com'
      register: cert
    - debug: msg="{{ cert }}"

'''


def main():
    argspec = hashivault_argspec()
    argspec['serial'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    module = hashivault_init(argspec)
    result = hashivault_pki_cert_revoke(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_cert_revoke(module):
    params = module.params
    client = hashivault_auth_client(params)

    serial = params.get('serial')
    mount_point = params.get('mount_point').strip('/')

    result = {"changed": False, "rc": 0}
    try:
        result['data'] = client.secrets.pki.revoke_certificate(serial_number=serial,
                                                               mount_point=mount_point).get('data')
    except Exception as e:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Exception: " + str(e)
    return result


if __name__ == '__main__':
    main()
