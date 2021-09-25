#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_oidc_auth_method_config
version_added: "4.1.1"
short_description: Hashicorp Vault OIDC auth method config
description:
    - Module to configure an OIDC auth mount
options:
    mount_point:
        description:
            - name of the secret engine mount name.
        default: oidc
    default_role:
        description:
            - The default role to use if none is provided during login.
    oidc_discovery_url:
        description:
            - The OIDC Discovery URL, without any .well-known component (base path). Cannot be used with "jwks_url" or
              "jwt_validation_pubkeys".
    oidc_client_id:
        description:
            - The OAuth Client ID from the provider for OIDC roles.
    oidc_client_secret:
        description:
            - The OAuth Client Secret from the provider for OIDC roles.
    bound_issuer:
        description:
            - The value against which to match the iss claim in a JWT.
    jwks_ca_pem:
        description:
            - The CA certificate or chain of certificates, in PEM format, to use to validate connections to the JWKS
              URL. If not set, system certificates are used.
    jwks_url:
        description:
            - JWKS URL to use to authenticate signatures. Cannot be used with "oidc_discovery_url" or
              "jwt_validation_pubkeys".
    jwt_supported_algs:
        description:
            - A list of supported signing algorithms.
        default: RS256
    jwt_validation_pubkeys:
        description:
            - A list of PEM-encoded public keys to use to authenticate signatures locally. Cannot be used with
              "jwks_url" or "oidc_discovery_url".
    oidc_discovery_ca_pem:
        description:
            - The CA certificate or chain of certificates, in PEM format, to use to validate connections to the OIDC
              Discovery URL. If not set, system certificates are used.
    provider_config:
        description:
            - "Configuration options for provider-specific handling.
              Providers with specific handling include: Azure, Google."
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_oidc_auth_method_config:
        oidc_discovery_url: "https://accounts.google.com"
        oidc_client_id: "123456"
        oidc_client_secret: "123456"
        default_role: "gmail"
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='oidc')
    argspec['bound_issuer'] = dict(required=False, type='str', default='')
    argspec['jwks_ca_pem'] = dict(required=False, type='str', default='')
    argspec['jwks_url'] = dict(required=False, type='str')
    argspec['jwt_supported_algs'] = dict(required=False, type='list', default=[])
    argspec['jwt_validation_pubkeys'] = dict(required=False, type='list', default=[])
    argspec['oidc_discovery_url'] = dict(required=False, type='str')
    argspec['oidc_discovery_ca_pem'] = dict(required=False, type='str', default='')
    argspec['oidc_client_id'] = dict(required=False, type='str')
    argspec['oidc_client_secret'] = dict(required=False, type='str')
    argspec['default_role'] = dict(required=False, type='str')
    argspec['provider_config'] = dict(required=False, type='dict')
    required_one_of = [['oidc_discovery_url', 'jwks_url']]
    module = hashivault_init(argspec, supports_check_mode=True, required_one_of=required_one_of)
    result = hashivault_oidc_auth_method_config(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_oidc_auth_method_config(module):
    params = module.params
    mount_point = params.get('mount_point').strip('/')
    client = hashivault_auth_client(params)
    parameters = [
        'bound_issuer',
        'jwks_ca_pem',
        'jwks_url',
        'jwt_supported_algs',
        'jwt_validation_pubkeys',
        'oidc_discovery_ca_pem',
        'oidc_discovery_url',
        'oidc_client_id',
        'oidc_client_secret',
        'default_role',
        'provider_config',
    ]
    desired_state = dict()
    for parameter in parameters:
        if params.get(parameter) is not None:
            desired_state[parameter] = params.get(parameter)
    desired_state['path'] = mount_point

    changed = False
    current_state = {}
    try:
        current_state = client.auth.oidc.read_config(path=mount_point)['data']
    except Exception:
        changed = True
    for key in desired_state.keys():
        current_value = current_state.get(key, None)
        if current_value is not None and current_value != desired_state[key]:
            changed = True
            break

    if changed and not module.check_mode:
        client.auth.oidc.configure(**desired_state)
    return {'changed': changed, 'old_state': current_state, 'new_state': desired_state}


if __name__ == '__main__':
    main()
