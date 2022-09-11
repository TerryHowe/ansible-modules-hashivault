#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
from hvac.exceptions import InvalidPath

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_auth_ldap
version_added: "3.17.7"
short_description: Hashicorp Vault ldap configuration module
description:
    - Module to configure the LDAP authentication method in Hashicorp Vault.
options:
    mount_point:
        description:
            - location where this auth_method is mounted. also known as "path"
    ldap_url:
        description:
            - The LDAP server to connect to. Examples: ldap://ldap.myorg.com
        default: ldap://127.0.0.1
    case_sensitive_names:
        description:
            - If set, user and group names assigned to policies within the backend will be case sensitive. Otherwise,
              names will be normalized to lower case. Case will still be preserved when sending the username to the LDAP
              server at login time; this is only for matching local user/group definitions.
        default: False
    starttls:
        description:
            - If true, issues a StartTLS command after establishing an unencrypted connection
        default: False
    tls_min_version:
        description:
            - Minimum TLS version to use. Accepted values are tls10, tls11 or tls12
        default: tls12
    tls_max_version:
        description:
            - Maximum TLS version to use. Accepted values are tls10, tls11 or tls12
        default: tls12
    insecure_tls:
        description:
            -  If true, skips LDAP server SSL certificate verification
        default: False
    certificate:
        description:
            - CA certificate to use when verifying LDAP server certificate, must be x509 PEM encoded
        default: ''
    bind_dn:
        description:
         - Distinguished name of object to bind when performing user search.
           Example cn=vault,ou=Users,dc=example,dc=com
        default: ''
    bind_pass:
        description:
            - Password to use along with binddn when performing user search
        default: None
    user_dn:
        description:
            - Base DN under which to perform user search. Example: ou=Users,dc=example,dc=com
        default: ''
    user_attr:
        description:
         - Attribute on user attribute object matching the username passed when authenticating.
           Examples sAMAccountName, cn, uid
        default: cn
    discover_dn:
        description:
         - Use anonymous bind to discover the bind DN of a user
        default: False
    deny_null_bind:
        description:
         - This option prevents users from bypassing authentication when providing an empty password
        default: True
    upn_domain:
        description:
         - The userPrincipalDomain used to construct the UPN string for the authenticating user
        default: ''
    group_filter:
        description:
            - Go template used when constructing the group membership query. The template can access the following
              context variables [UserDN, Username]
        default: (|(memberUid={{.Username}})(member={{.UserDN}})(uniqueMember={{.UserDN}}))
    group_attr:
        description:
            - LDAP attribute to follow on objects returned by groupfilter in order to enumerate user group membership
        default: 'cn'
    group_dn:
        description:
            - LDAP search base to use for group membership search
        default: ''
    token_ttl:
        description:
            - The incremental lifetime for generated tokens
        default: ''
    token_max_ttl:
        description:
            - The maximum lifetime for generated tokens
        default: ''
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_ldap:
        user_dn: "{{ auth_ldap_userdn }}"
        group_dn: "{{ auth_ldap_groupdn }}"
        bind_dn: "{{ auth_ldap_binddn }}"
        ldap_url: "{{ auth_ldap_url }}"
        insecure_tls: "{{ auth_ldap_insecure_tls }}"
        group_filter: "{{ auth_ldap_groupfilter }}"
        upn_domain: "{{ auth_ldap_upndomain }}"
'''


def main():
    # separate long default value to pass linting
    default_group_filter = '(|(memberUid={{.Username}})(member={{.UserDN}})(uniqueMember={{.UserDN}}))'
    argspec = hashivault_argspec()
    argspec['description'] = dict(required=False, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='ldap')
    argspec['ldap_url'] = dict(required=False, type='str', default='ldap://127.0.0.1')
    argspec['case_sensitive_names'] = dict(required=False, type='bool', default=False)
    argspec['starttls'] = dict(required=False, type='bool', default=False)
    argspec['tls_min_version'] = dict(required=False, type='str', default='tls12')
    argspec['tls_max_version'] = dict(required=False, type='str', default='tls12')
    argspec['insecure_tls'] = dict(required=False, type='bool', default=False)
    argspec['certificate'] = dict(required=False, type='str', default='')
    argspec['bind_dn'] = dict(required=False, type='str', default='')
    argspec['bind_pass'] = dict(required=False, type='str', default=None, no_log=True)
    argspec['user_attr'] = dict(required=False, type='str', default='cn')
    argspec['user_dn'] = dict(required=False, type='str', default='')
    argspec['discover_dn'] = dict(required=False, type='bool', default=False)
    argspec['deny_null_bind'] = dict(required=False, type='bool', default=True)
    argspec['upn_domain'] = dict(required=False, type='str', default='')
    argspec['group_filter'] = dict(required=False, type='str', default=default_group_filter)
    argspec['group_attr'] = dict(required=False, type='str', default='cn')
    argspec['group_dn'] = dict(required=False, type='str', default='')
    argspec['use_token_groups'] = dict(required=False, type='bool', default=False)
    argspec['token_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_max_ttl'] = dict(required=False, type='int', default=0)

    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_auth_ldap(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_auth_ldap(module):
    params = module.params
    client = hashivault_auth_client(params)
    changed = False
    desired_state = dict()
    desired_state['mount_point'] = params.get('mount_point')
    desired_state['url'] = params.get('ldap_url')
    desired_state['case_sensitive_names'] = params.get('case_sensitive_names')
    desired_state['starttls'] = params.get('starttls')
    desired_state['tls_min_version'] = params.get('tls_min_version')
    desired_state['tls_max_version'] = params.get('tls_max_version')
    desired_state['insecure_tls'] = params.get('insecure_tls')
    desired_state['certificate'] = params.get('certificate')
    desired_state['bind_dn'] = params.get('bind_dn')
    desired_state['bind_pass'] = params.get('bind_pass')
    desired_state['user_attr'] = params.get('user_attr')
    desired_state['user_dn'] = params.get('user_dn')
    desired_state['discover_dn'] = params.get('discover_dn')
    desired_state['deny_null_bind'] = params.get('deny_null_bind')
    desired_state['upn_domain'] = params.get('upn_domain')
    desired_state['group_filter'] = params.get('group_filter')
    desired_state['group_attr'] = params.get('group_attr')
    desired_state['group_dn'] = params.get('group_dn')
    desired_state['use_token_groups'] = params.get('use_token_groups')
    desired_state['token_ttl'] = params.get('token_ttl')
    desired_state['token_max_ttl'] = params.get('token_max_ttl')

    # if bind pass is None, remove it from desired state since we can't compare
    if desired_state['bind_pass'] is None:
        del desired_state['bind_pass']

    # check current config
    current_state = dict()
    try:
        result = client.auth.ldap.read_configuration(
            mount_point=desired_state['mount_point'])['data']
        # some keys need to be remapped to match desired state (and HVAC implementation)
        current_state['discover_dn'] = result['discoverdn']
        current_state['group_attr'] = result['groupattr']
        current_state['user_attr'] = result['userattr']
        current_state['group_dn'] = result['groupdn']
        current_state['upn_domain'] = result['upndomain']
        current_state['group_filter'] = result['groupfilter']
        current_state['case_sensitive_names'] = result['case_sensitive_names']
        current_state['certificate'] = result['certificate']
        current_state['tls_max_version'] = result['tls_max_version']
        current_state['tls_min_version'] = result['tls_min_version']
        current_state['insecure_tls'] = result['insecure_tls']
        current_state['deny_null_bind'] = result['deny_null_bind']
        current_state['user_dn'] = result['userdn']
        current_state['bind_dn'] = result['binddn']
        current_state['use_token_groups'] = result['use_token_groups']
        current_state['url'] = result['url']
        current_state['starttls'] = result['starttls']
        current_state['token_ttl'] = result['token_ttl']
        current_state['token_max_ttl'] = result['token_max_ttl']
    except InvalidPath:
        pass

    # check if current config matches desired config values, if they match, set changed to false to prevent action
    for k, v in current_state.items():
        if v != desired_state[k]:
            changed = True

    # if configs dont match and checkmode is off, complete the change
    if changed and not module.check_mode:
        client.auth.ldap.configure(**desired_state)

    return {'changed': changed}


if __name__ == '__main__':
    main()
