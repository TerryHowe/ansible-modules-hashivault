#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_cert_sign
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Sign CSR ( Certificate / Intermediate / Verbatim )
description:
    - This module signs a new certificate based upon the provided CSR and the supplied parameters.
options:
    csr:
        recuired: true
        description:
            - Specifies the PEM-encoded CSR.
    role:
        description:
            - Specifies the name of the role to create.
            - 'For *verbatim* type if set, the following parameters from the role will have effect: `ttl`, `max_ttl`,
              `generate_lease`, and `no_store`.'
    common_name:
        description:
            - Specifies the requested CN for the certificate. If the CN is allowed by role policy, it will be issued.
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
    type:
        type: str
        description:
            - Sign a new certificate with `certificate` based upon the provided CSR and the supplied parameters, subject
              to the restrictions contained in the role named in the endpoint. The issuing CA certificate is returned as
              well, so that only the root CA need be in a client's trust store.
            - Use `intermediate` to configure CA certificate to issue a certificate with appropriate values for
              acting as an intermediate CA. Distribution points use the values set via config/urls. Values set in the
              CSR are ignored unless use_csr_values is set to true, in which case the values from the CSR are used
              verbatim.
            - Use `verbatim` to sign a new certificate based upon the provided CSR. Values are taken verbatim from the
              CSR; the only restriction is that this endpoint will refuse to issue an intermediate CA certificate (use
              `intermediate` type for that functionality.)
        choices: ["certificate", "intermediate", "verbatim"]
        default: certificate
    extra_params:
        description:
            Extra parameters depending on the type.
        type: dict
extends_documentation_fragment:
    - hashivault
'''

EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - hashivault_pki_cert_sign:
        role: 'tester'
        common_name: 'test.example.com'
      register: cert
    - debug: msg="{{ cert }}"

'''


def main():
    argspec = hashivault_argspec()
    argspec['csr'] = dict(required=True, type='str')
    argspec['role'] = dict(required=False, type='str')
    argspec['common_name'] = dict(required=False, type='str')
    argspec['extra_params'] = dict(required=False, type='dict', default={})
    argspec['mount_point'] = dict(required=False, type='str', default='pki')
    argspec['type'] = dict(required=False, type='str', default='certificate', choices=["certificate", "intermediate",
                                                                                       "verbatim"])

    module = hashivault_init(argspec)
    result = hashivault_pki_cert_sign(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def certificate(params, mount_point, client):
    csr = params.get('csr')
    common_name = params.get('common_name')
    extra_params = params.get('extra_params')
    role = params.get('role').strip('/')

    # check if role exists
    try:
        current_state = client.secrets.pki.read_role(name=role, mount_point=mount_point).get('data')
    except Exception:
        current_state = {}
    if not current_state:
        return {'failed': True, 'rc': 1, 'msg': 'role not found or permission denied'}

    if not common_name:
        return {'failed': True, 'rc': 1, 'msg': 'Missing required options: common_name'}

    result = {"changed": False, "rc": 0}
    try:
        result['data'] = client.secrets.pki.sign_certificate(csr=csr, name=role, mount_point=mount_point,
                                                             common_name=common_name,
                                                             extra_params=extra_params).get('data')
        result['changed'] = True
    except Exception as e:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Exception: " + str(e)
    return result


def intermediate(params, mount_point, client):
    csr = params.get('csr')
    common_name = params.get('common_name')
    extra_params = params.get('extra_params')

    if not common_name:
        return {'failed': True, 'rc': 1, 'msg': 'Missing required options: common_name'}

    result = {"changed": False, "rc": 0}
    try:
        result['data'] = client.secrets.pki.sign_intermediate(csr=csr, common_name=common_name,
                                                              extra_params=extra_params,
                                                              mount_point=mount_point).get('data')
        result['changed'] = True
    except Exception as e:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Exception: " + str(e)
    return result


def verbatim(params, mount_point, client):
    csr = params.get('csr')
    extra_params = params.get('extra_params')
    role = params.get('role').strip('/')

    # check if role exists
    try:
        current_state = client.secrets.pki.read_role(name=role, mount_point=mount_point).get('data')
    except Exception:
        current_state = {}
    if not current_state:
        return {'failed': True, 'rc': 1, 'msg': 'role not found or permission denied'}

    result = {"changed": False, "rc": 0}
    try:
        result['data'] = client.secrets.pki.sign_verbatim(csr=csr, name=role, extra_params=extra_params,
                                                          mount_point=mount_point).get('data')
        result['changed'] = True
    except Exception as e:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Exception: " + str(e)
    return result


@hashiwrapper
def hashivault_pki_cert_sign(module):
    supported_types = {
        'certificate': certificate,
        'intermediate': intermediate,
        'verbatim': verbatim
    }
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point').strip('/')

    return supported_types[params.get('type')](params=params, mount_point=mount_point, client=client)


if __name__ == '__main__':
    main()
