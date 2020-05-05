#!/usr/bin/env python
from ansible.module_utils.hashivault import check_secrets_engines
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_set_signed
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Set Signed Intermediate
description:
    - This module allows submitting the signed CA certificate corresponding to a private key generated via
      `intermediate` type in `hashivault_pki_ca` module.
    - The certificate should be submitted in PEM format.
options:
    certificate:
        recuired: true
        type: str
        description:
            - Specifies the name of the role to create.
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
    - name: Generate Intermediate
      hashivault_pki_ca:
        mount_point: "{{mount_inter}}"
        common_name: my common name
        kind: intermediate
      register: response
    - name: List Certificates
      hashivault_pki_cert_list:
        mount_point: "{{mount_inter}}"
      register: list
    - name: Sign Intermediate
      hashivault_pki_cert_sign:
        mount_point: "{{mount_root}}"
        csr: "{{response.data.csr}}"
        common_name: my common name
        type: intermediate
      register: response
    - name: Set Signed Intermediate
      hashivault_pki_set_signed:
        mount_point: "{{mount_inter}}"
        certificate: "{{ response.data.certificate }}\n{{ response.data.issuing_ca }}"

'''


def main():
    argspec = hashivault_argspec()
    argspec['certificate'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    module = hashivault_init(argspec)
    result = hashivault_pki_set_signed(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_set_signed(module):
    params = module.params
    client = hashivault_auth_client(params)

    certificate = params.get('certificate')
    mount_point = params.get('mount_point').strip('/')

    # check if engine is enabled
    _, err = check_secrets_engines(module, client)
    if err:
        return err

    result = {"changed": False, "rc": 0}
    try:
        result['changed'] = client.secrets.pki.set_signed_intermediate(certificate=certificate,
                                                                       mount_point=mount_point).ok
    except Exception as e:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Exception: " + str(e)
    return result


if __name__ == '__main__':
    main()
