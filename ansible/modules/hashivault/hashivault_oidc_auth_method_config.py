#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json, sys
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
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    ca_cert:
        description:
            - "path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate"
        default: to environment variable VAULT_CACERT
    ca_path:
        description:
            - "path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate : if ca_cert
             is specified, its value will take precedence"
        default: to environment variable VAULT_CAPATH
    client_cert:
        description:
            - "path to a PEM-encoded client certificate for TLS authentication to the Vault server"
        default: to environment variable VAULT_CLIENT_CERT
    client_key:
        description:
            - "path to an unencrypted PEM-encoded private key matching the client certificate"
        default: to environment variable VAULT_CLIENT_KEY
    verify:
        description:
            - "if set, do not verify presented TLS certificate before communicating with Vault server : setting this
             variable is not recommended except during testing"
        default: to environment variable VAULT_SKIP_VERIFY
    authtype:
        description:
            - "authentication type to use: token, userpass, github, ldap, approle"
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
        default: to environment variable VAULT_USER
    password:
        description:
            - password to login to vault.
        default: to environment variable VAULT_PASSWORD
    namespace:
        description:
            - namespace for vault
        default: to environment variable VAULT_NAMESPACE
    mount_point:
        description:
            - name of the secret engine mount name.
        default: oidc
    default_role:
        description:
            - The default role to use if none is provided during login.
    oidc_discovery_url:
        description:
            - The OIDC Discovery URL, without any .well-known component (base path). Cannot be used with "jwks_url" or "jwt_validation_pubkeys".
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
            - The CA certificate or chain of certificates, in PEM format, to use to validate connections to the JWKS URL. If not set, system certificates are used.
    jwks_url:
        description:
            - JWKS URL to use to authenticate signatures. Cannot be used with "oidc_discovery_url" or "jwt_validation_pubkeys".
    jwt_supported_algs:
        description:
            - A list of supported signing algorithms.
        default: RS256
    jwt_validation_pubkeys:
        description:
            - A list of PEM-encoded public keys to use to authenticate signatures locally. Cannot be used with "jwks_url" or "oidc_discovery_url".
    oidc_discovery_ca_pem:
        description: 
            - The CA certificate or chain of certificates, in PEM format, to use to validate connections to the OIDC Discovery URL. If not set, system certificates are used.
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
    supports_check_mode=True
    required_one_of=[['oidc_discovery_url', 'jwks_url']]
    module = hashivault_init(argspec, supports_check_mode, required_one_of=required_one_of)
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
    mount_point = params.get('mount_point')
    desired_state = dict()
    current_state = dict()
    exists = False

    token = params['token'] 
    namespace = params['namespace']
    headers = {'X-Vault-Token': token, 'X-Vault-Namespace': namespace}
    url = params['url']
    verify = params['verify']

    # do not want a trailing slash in mount_point
    if mount_point[-1]:
        mount_point = mount_point.strip('/')

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

    # check if engine is enabled
    try:
      if (mount_point + "/") not in client.sys.list_auth_methods()['data'].keys():
        return {'failed': True, 'msg': 'auth mount is not enabled', 'rc': 1}
    except:
      if module.check_mode:
        changed = True
      else:
        return {'failed': True, 'msg': 'auth mount is not enabled', 'rc': 1}

    # check if any config exists
    try:
        current_state = requests.get(url + '/v1/auth/' + mount_point + '/config', verify=verify, headers=headers)
        if current_state.status_code == 404:
            changed = True
        elif current_state.status_code == 200:
            exists = True
    except: 
        changed = True
     
    # check if current config matches desired config values, if they dont match, set changed true
    if exists:
      current_state = current_state.json()['data']
      for k, v in current_state.items():
        if v != desired_state[k]:
            changed = True
    
    desired_state['oidc_client_secret'] = params.get('oidc_client_secret') 

    # if configs dont match and checkmode is off, complete the change
    if changed == True and not module.check_mode:
         config_status = requests.post(url + '/v1/auth/' + mount_point + '/config', verify=verify, headers=headers, json=desired_state) 
         try:
            config_status.raise_for_status()
         except: 
            return {'failed': True, 'msg': config_status.text, 'rc': 1}
    return {'changed': changed}


if __name__ == '__main__':
    main()
