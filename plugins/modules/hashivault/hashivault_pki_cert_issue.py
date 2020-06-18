#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import check_secrets_engines
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import check_pki_role
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_cert_issue
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Generate Certificate
description:
    - This module generates a new set of credentials (private key and certificate) based on the role named in the
      module.
    - The issuing CA certificate is returned as well, so that only the root CA need be in a client's trust store.
options:
    role:
        recuired: true
        description:
            - Specifies the name of the role to create.
    common_name:
        recuired: true
        description:
            - Specifies the requested CN for the certificate. If the CN is allowed by role policy, it will be issued.
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
    extra_params:
        description:
            - "Collection of properties from pki role U(https://www.vaultproject.io/api-docs/secret/pki#parameters-6)"
        type: dict
        suboptions:
        alt_names:
            type: string
            description:
                - Specifies requested Subject Alternative Names, in a comma-delimited list. These can be host names or
                  email addresses; they will be parsed into their respective fields. If any requested names do not match
                  role policy, the entire request will be denied.
        ip_sans:
            type: string
            description:
                - Specifies requested IP Subject Alternative Names, in a comma-delimited list. Only valid if the role
                  allows IP SANs (which is the default).
        uri_sans:
            type: string
            description:
                - Specifies the requested URI Subject Alternative Names, in a comma-delimited list.
        other_sans:
            type: string
            description:
                - Specifies custom OID/UTF8-string SANs. These must match values specified on the role in
                  allowed_other_sans (see role creation for allowed_other_sans globbing rules). The format is the same
                  as OpenSSL <oid>;<type>:<value> where the only current valid type is UTF8. This can be a
                  comma-delimited list or a JSON string slice.
        ttl:
            type: string
            description:
                - Specifies requested Time To Live. Cannot be greater than the role's max_ttl value. If not provided,
                  the role's ttl value will be used. Note that the role values default to system values if not
                  explicitly set.
        format:
            type: string
            description:
                - Specifies the format for returned data. Can be pem, der, or pem_bundle; defaults to pem. If der, the
                  output is base64 encoded. If pem_bundle, the certificate field will contain the private key and
                  certificate, concatenated; if the issuing CA is not a Vault-derived self-signed root, this will be
                  included as well.
        private_key_format:
            type: string
            description:
                - Specifies the format for marshaling the private key. Defaults to der which will return either
                  base64-encoded DER or PEM-encoded DER, depending on the value of format. The other option is pkcs8
                  which will return the key marshalled as PEM-encoded PKCS8.
        exclude_cn_from_sans:
            type: bool
            description:
                - If true, the given common_name will not be included in DNS or Email Subject Alternate Names
                  (as appropriate). Useful if the CN is not a hostname or email address, but is instead some
                  human-readable identifier.
extends_documentation_fragment:
    - hashivault
'''

EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - hashivault_pki_cert_issue:
        role: 'tester'
        common_name: 'test.example.com'
      register: cert
    - debug: msg="{{ cert }}"

'''


def main():
    argspec = hashivault_argspec()
    argspec['role'] = dict(required=True, type='str')
    argspec['common_name'] = dict(required=True, type='str')
    argspec['extra_params'] = dict(required=False, type='dict', default={})
    argspec['mount_point'] = dict(required=False, type='str', default='pki')

    module = hashivault_init(argspec)
    result = hashivault_pki_cert_issue(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_cert_issue(module):
    params = module.params
    client = hashivault_auth_client(params)

    role = params.get('role').strip('/')
    common_name = params.get('common_name')
    extra_params = params.get('extra_params')
    mount_point = params.get('mount_point').strip('/')

    # check if engine is enabled
    _, err = check_secrets_engines(module, client)
    if err:
        return err

    if not check_pki_role(name=role, mount_point=mount_point, client=client):
        return {'failed': True, 'rc': 1, 'msg': 'role not found or permission denied'}

    result = {"changed": False, "rc": 0}
    try:
        result['data'] = client.secrets.pki.generate_certificate(name=role, common_name=common_name,
                                                                 extra_params=extra_params,
                                                                 mount_point=mount_point).get('data')
    except Exception as e:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Exception: " + str(e)
    return result


if __name__ == '__main__':
    main()
