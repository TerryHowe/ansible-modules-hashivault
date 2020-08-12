#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import requests

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
        verify: False
'''


def main():
    argspec = hashivault_argspec()
    argspec['bound_issuer'] = dict(required=False, type='str', default='')
    argspec['jwks_ca_pem'] = dict(required=False, type='str', default='')
    argspec['jwks_url'] = dict(required=False, type='str')
    argspec['jwt_supported_algs'] = dict(required=False, type='list', default=[])
    argspec['jwt_validation_pubkeys'] = dict(required=False, type='list', default=[])
    argspec['oidc_discovery_ca_pem'] = dict(required=False, type='str', default='')
    argspec['mount_point'] = dict(required=False, type='str', default='oidc')
    argspec['oidc_discovery_url'] = dict(required=False, type='str')
    argspec['oidc_client_id'] = dict(required=False, type='str')
    argspec['oidc_client_secret'] = dict(required=False, type='str')
    argspec['default_role'] = dict(required=False, type='str')
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
    client = hashivault_auth_client(params)
    changed = False
    mount_point = params.get('mount_point').strip('/')
    desired_state = dict()
    current_state = dict()
    exists = False

    token = params.get('token', client.token)
    namespace = params['namespace']
    headers = {'X-Vault-Token': token, 'X-Vault-Namespace': namespace}
    url = params['url']
    verify = params['verify']

    if not params.get('oidc_discovery_url'):
        desired_state['oidc_discovery_url'] = ''
    else:
        desired_state['oidc_discovery_url'] = params.get('oidc_discovery_url')
    desired_state['oidc_client_id'] = params.get('oidc_client_id')
    desired_state['default_role'] = params.get('default_role')
    desired_state['bound_issuer'] = params.get('bound_issuer')
    desired_state['jwks_ca_pem'] = params.get('jwks_ca_pem')
    if not params.get('jwks_url'):
        desired_state['jwks_url'] = ''
    else:
        desired_state['jwks_url'] = params.get('jwks_url')
    desired_state['jwt_supported_algs'] = params.get('jwt_supported_algs')
    desired_state['jwt_validation_pubkeys'] = params.get('jwt_validation_pubkeys')
    desired_state['oidc_discovery_ca_pem'] = params.get('oidc_discovery_ca_pem')

    # check if any config exists
    try:
        current_state = requests.get(url + '/v1/auth/' + mount_point + '/config', verify=verify, headers=headers)
        if current_state.status_code == 404:
            changed = True
        elif current_state.status_code == 200:
            exists = True
    except Exception:
        changed = True

    # check if current config matches desired config values, if they dont match, set changed true
    if exists:
        current_state = current_state.json()['data']
        for k, v in current_state.items():
            if k in desired_state and v != desired_state[k]:
                changed = True

    desired_state['oidc_client_secret'] = params.get('oidc_client_secret')

    # if configs dont match and checkmode is off, complete the change
    if changed and not module.check_mode:
        config_status = requests.post(url + '/v1/auth/' + mount_point + '/config', verify=verify, headers=headers,
                                      json=desired_state)
        try:
            config_status.raise_for_status()
        except Exception:
            return {'failed': True, 'msg': config_status.text, 'rc': 1}
    return {'changed': changed}


if __name__ == '__main__':
    main()
