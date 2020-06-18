#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_tidy
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Tidy
description:
    - This endpoint retrieves one of a selection of certificates.
options:
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
    config:
        type: dict
        description:
            - Collection of properties for pki tidy endpoint. Ref.
              U(https://www.vaultproject.io/api-docs/secret/pki#tidy)
        suboptions:
            tidy_cert_store:
                type: bool
                default: false
                description:
                    - Specifies whether to tidy up the certificate store.
            tidy_revoked_certs:
                type: bool
                default: false
                description:
                    - Set to true to expire all revoked and expired certificates, removing them both from the CRL and
                      from storage.
                    - The CRL will be rotated if this causes any values to be removed.
            safety_buffer:
                type: str
                default: 72h
                description:
                    - Specifies A duration used as a safety buffer to ensure certificates are not expunged prematurely;
                    - as an example, this can keep certificates from being removed from the CRL that, due to clock skew,
                      might still be considered valid on other hosts.
                    - For a certificate to be expunged, the time must be after the expiration time of the certificate
                      (according to the local clock) plus the duration of safety_buffer.
extends_documentation_fragment:
    - hashivault
'''

EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - hashivault_pki_tidy:
        safety_buffer: 96h
        tidy_revoked_certs: true
'''


def main():
    argspec = hashivault_argspec()
    argspec['config'] = dict(required=False, type='dict', default={})
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    module = hashivault_init(argspec)
    result = hashivault_pki_tidy(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_tidy(module):
    params = module.params
    client = hashivault_auth_client(params)

    config = params.get('config')
    mount_point = params.get('mount_point').strip('/')

    result = {"changed": False, "rc": 0}
    try:
        client.secrets.pki.tidy(extra_params=config, mount_point=mount_point)
    except Exception as e:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Exception: " + str(e)
    return result


if __name__ == '__main__':
    main()
