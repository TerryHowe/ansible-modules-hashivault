#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
from hvac.constants.ldap import DEFAULT_GROUP_FILTER

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_auth_method
version_added: "3.17.7"
short_description: Hashicorp Vault ldap configuration module
description:
    - Module to configure the LDAP authentication method in Hashicorp Vault.
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
    mount_point:
        description:
            - location where this auth_method is mounted. also known as "path"
    config:
        description:
            - configuration set on auth method. expects a dict
        default: "{
            'url': 'ldap://127.0.0.1', 'case_sensitive_names': False, 'starttls': False, 
            'tls_min_version': 'tls12', 'tls_max_version': 'tls12', 'insecure_tls': False,
            'certificate': None, 'bind_dn': None, 'bind_pass': None, 'user_attr': 'cn',
            'discover_dn': False, 'deny_null_bind': True, 'upn_domain': None,
            'group_filter': '(|(memberUid={{.Username}})(member={{.UserDN}})(uniqueMember={{.UserDN}}))',
            'group_attr': 'cn'}"
        
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_ldap:
        config: 
            user_dn: "{{ auth_ldap_userdn }}"
            group_dn: "{{ auth_ldap_groupdn }}"
            bind_dn: "{{ auth_ldap_binddn }}"
            url: "{{ auth_ldap_url }}"
            insecure_tls: "{{ auth_ldap_insecure_tls }}"
            group_filter: "{{ auth_ldap_groupfilter }}"
            upn_domain: "{{ auth_ldap_upndomain }}"
        token: "{{ vault_token }}"
        url: "{{ vault_url }}"
'''

DEFAULT_URL = 'ldap://127.0.0.1'
DEFAULT_CASE_SENSITIVE_NAMES = False
DEFAULT_STARTTLS = False
DEFAULT_TLS_MIN_VERSION = 'tls12'
DEFAULT_TLS_MAX_VERSION = 'tls12'
DEFAULT_INSECURE_TLS = False
DEFAULT_CERTIFICATE = None
DEFAULT_BIND_DN = None
DEFAULT_BIND_PASS = None
DEFAULT_USER_ATTR = 'cn'
DEFAULT_DISCOVER_DN = False
DEFAULT_DENY_NULL_BIND = True
DEFAULT_UPN_DOMAIN = None
DEFAULT_GROUP_FILTER = DEFAULT_GROUP_FILTER
DEFAULT_GROUP_ATTR = 'cn'
DEFAULT_MOUNT_POINT = 'ldap'

def main():
    argspec = hashivault_argspec()
    argspec['description'] = dict(required=False, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default=None)
    argspec['config'] = dict(required=False, type='dict', default=None)
    module = hashivault_init(argspec)
    result = hashivault_auth_ldap(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)

@hashiwrapper
def hashivault_auth_ldap(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point')
    config = params.get('config')
    exists = False
    changed = False

    if mount_point == None:
        mount_point = DEFAULT_MOUNT_POINT
    
    auth_methods = client.sys.list_auth_methods()
    path = (mount_point) + u"/"

    # Is auth method enabled already?
    if path in auth_methods['data'].keys():
        exists = True

    # If the auth method isn't enabled
    if exists == False:
        return {'msg': 'auth method isn\'t enabled'}

    if 'url' not in config:
        config['url'] = DEFAULT_URL
    if 'case_sensitive_names' not in config:
        config['case_sensitive_names'] = DEFAULT_CASE_SENSITIVE_NAMES
    if 'starttls' not in config:
        config['starttls'] = DEFAULT_STARTTLS
    if 'tls_min_version' not in config:
        config['tls_min_version'] = DEFAULT_TLS_MIN_VERSION
    if 'tls_max_version' not in config:
        config['tls_max_version'] = DEFAULT_TLS_MAX_VERSION
    if 'insecure_tls' not in config:
        config['insecure_tls'] = DEFAULT_INSECURE_TLS
    if 'certificate' not in config:
        config['certificate'] = DEFAULT_CERTIFICATE
    if 'bind_dn' not in config:
        config['bind_dn'] = DEFAULT_BIND_DN
    if 'bind_pass' not in config:
        config['bind_pass'] = DEFAULT_BIND_PASS
    if 'user_attr' not in config:
        config['user_attr'] = DEFAULT_USER_ATTR
    if 'discover_dn' not in config:
        config['discover_dn'] = DEFAULT_DISCOVER_DN
    if 'deny_null_bind' not in config:
        config['deny_null_bind'] = DEFAULT_DENY_NULL_BIND
    if 'upn_domain' not in config:
        config['upn_domain'] = DEFAULT_UPN_DOMAIN
    if 'group_filter' not in config:
        config['group_filter'] = DEFAULT_GROUP_FILTER
    if 'group_attr' not in config:
        config['group_attr'] = DEFAULT_GROUP_ATTR

    # configure the ldap method
    client.auth.ldap.configure(
        user_dn=config['user_dn'], 
        group_dn=config['group_dn'],
        url=config['url'],
        case_sensitive_names=config['case_sensitive_names'],
        starttls=config['starttls'],
        tls_min_version=config['tls_min_version'],
        tls_max_version=config['tls_max_version'],
        insecure_tls=config['insecure_tls'],
        certificate=config['certificate'],
        bind_dn=config['bind_dn'],
        bind_pass=config['bind_pass'],
        user_attr=config['user_attr'],
        discover_dn=config['discover_dn'],
        deny_null_bind=config['deny_null_bind'],
        upn_domain=config['upn_domain'],
        group_filter=config['group_filter'],
        group_attr=config['group_attr'],
        mount_point=mount_point)
    
    return {'changed': changed}

if __name__ == '__main__':
    main()