#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_ca_set
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Submit CA Information
description:
    - This module allows submitting the CA information for the backend via a PEM file containing the CA certificate and
      its private key, concatenated.
    - May optionally append additional CA certificates. Useful when creating an intermediate CA to ensure a full chain
      is returned when signing or generating certificates.
    - Not needed if you are generating a self-signed root certificate, and not used if you have a signed intermediate
      CA certificate with a generated key, use the hashivault_pki_set_signed for that. If you have already set a
      certificate and key, they will be overridden.
options:
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
    pem_bundle:
        required: true
        type: str
        description:
        - Specifies the key and certificate concatenated in PEM format.
extends_documentation_fragment:
    - hashivault
'''
EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - hashivault_pki_ca_set:
        pem_bundle: '-----BEGIN RSA PRIVATE KEY-----\n...\n-----END CERTIFICATE-----'
'''


def main():
    argspec = hashivault_argspec()
    argspec['pem_bundle'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_pki_ca_set(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_ca_set(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point').strip('/')
    pem_bundle = params.get('pem_bundle')

    if module.check_mode:
        return {'changed': True}

    result = {'changed': True}
    data = client.secrets.pki.submit_ca_information(pem_bundle=pem_bundle, mount_point=mount_point)
    if data:
        from requests.models import Response
        if isinstance(data, Response):
            result['data'] = data.text
        else:
            result['data'] = data

    return result


if __name__ == '__main__':
    main()
