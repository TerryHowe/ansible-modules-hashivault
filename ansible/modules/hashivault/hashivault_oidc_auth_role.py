#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import requests

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_oidc_auth_role
version_added: "4.1.1"
short_description: Hashicorp Vault OIDC secret engine role
description:
    - Module to define an OIDC role that vault can generate dynamic credentials for vault
options:
    mount_point:
        description:
            - name of the secret engine mount name.
        default: oidc
    name:
        description:
            - name of the role in vault
    bound_audiences:
        description:
            - List of `aud` claims to match against. Any match is sufficient.
    user_claim:
        description:
            - The claim to use to uniquely identify the user; this will be used as the name for the Identity entity
              alias created due to a successful login. The claim value must be a string.
        default: sub
    bound_subject:
        description:
            - If set, requires that the sub claim matches this value.
    bound_claims:
        description:
            - If set, a map of claims/values to match against. The expected value may be a single string or a list of
              strings.
    groups_claim:
        description:
            - The claim to use to uniquely identify the set of groups to which the user belongs; this will be used as
              the names for the Identity group aliases created due to a successful login. The claim value must be a
              list of strings.
    claim_mappings:
        description:
            - If set, a map of claims (keys) to be copied to specified metadata fields (values).
    oidc_scopes:
        description:
            - If set, a list of OIDC scopes to be used with an OIDC role. The standard scope "openid" is automatically
              included and need not be specified.
    allowed_redirect_uris:
        description:
            - The list of allowed values for redirect_uri during OIDC logins.
            - When using nested namespaces, use url encoding '%2F' instead of '/'
    token_ttl:
        description:
            - The incremental lifetime for generated tokens. This current value of this will be referenced at renewal
              time.
    token_max_ttl:
        description:
            - The maximum lifetime for generated tokens. This current value of this will be referenced at renewal time.
    token_policies:
        description:
            - List of policies to encode onto generated tokens. Depending on the auth method, this list may be
              supplemented by user/group/other values.
    token_bound_cidrs:
        description:
            - List of CIDR blocks; if set, specifies blocks of IP addresses which can authenticate successfully, and
              ties the resulting token to these blocks as well.
    token_explicit_max_ttl:
        description:
            - If set, will encode an explicit max TTL onto the token. This is a hard cap even if token_ttl and
              token_max_ttl would otherwise allow a renewal.
    token_no_default_policy:
        description:
            - If set, the default policy will not be set on generated tokens; otherwise it will be added to the policies
              set in token_policies.
    token_num_uses:
        description:
            - The maximum number of times a generated token may be used (within its lifetime); 0 means unlimited.
    token_period:
        description:
            - If set, indicates that the token generated using this role should never expire. The token should be
              renewed within the duration specified by this value. At each renewal, the token's TTL will be set to
              the value of this parameter.
    token_type:
        description:
            - The type of token that should be generated. Can be service, batch, or default to use the mount's tuned
              default (which unless changed will be service tokens). For token store roles, there are two additional
              possibilities (default-service and default-batch) which specify the type to return unless the client
              requests a different type at generation time.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_oidc_auth_role:
        name: "gmail"
        bound_audiences: ["123-456.apps.googleusercontent.com"]
        allowed_redirect_uris: ["https://vault.com:8200/ui/vault/auth/oidc/oidc/callback"]
        token_policies: ["test"]

- hosts: localhost
  tasks:
    - hashivault_oidc_auth_role:
        name: "nested_ns_role"
        bound_audiences: ["123-456.apps.googleusercontent.com"]
        allowed_redirect_uris: ["https://vault.com:8200/ui/oidc/oidc/callback?namespace=namespaceone%2Fnamespacetwo"]
        token_policies: ["test"]
'''


def main():
    argspec = hashivault_argspec()
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='oidc')
    argspec['user_claim'] = dict(required=False, type='str', default='sub')
    argspec['allowed_redirect_uris'] = dict(required=True, type='list')
    argspec['bound_audiences'] = dict(required=False, type='list', default=[])
    argspec['bound_subject'] = dict(required=False, type='str', default='')
    argspec['bound_claims'] = dict(required=False, type='dict')
    argspec['groups_claim'] = dict(required=False, type='str', default='')
    argspec['claim_mappings'] = dict(required=False, type='dict')
    argspec['oidc_scopes'] = dict(required=False, type='list', default=[])
    argspec['token_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_max_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_policies'] = dict(required=False, type='list', default=[])
    argspec['policies'] = dict(required=False, type='list', default=[])
    argspec['token_bound_cidrs'] = dict(required=False, type='list', default=[])
    argspec['token_explicit_max_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_no_default_policy'] = dict(required=False, type='bool', default=False)
    argspec['token_num_uses'] = dict(required=False, type='int', default=0)
    argspec['token_period'] = dict(required=False, type='int', default=0)
    argspec['token_type'] = dict(required=False, type='str', default='default')
    argspec['clock_skew_leeway'] = dict(required=False, type='int', default=0)
    argspec['expiration_leeway'] = dict(required=False, type='int', default=0)
    argspec['not_before_leeway'] = dict(required=False, type='int', default=0)

    module = hashivault_init(argspec)
    result = hashivault_oidc_auth_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_oidc_auth_role(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point').strip('/')
    name = params.get('name').strip('/')
    state = params.get('state')
    desired_state = dict()
    current_state = dict()
    changed = False

    token = params.get('token', client.token)
    namespace = params['namespace']
    headers = {'X-Vault-Token': token, 'X-Vault-Namespace': namespace}
    url = params['url']
    verify = params['verify']
    ca_cert = params['ca_cert']
    ca_path = params['ca_path']

    desired_state['allowed_redirect_uris'] = params.get('allowed_redirect_uris')
    desired_state['bound_audiences'] = params.get('bound_audiences')
    desired_state['bound_claims'] = params.get('bound_claims')
    desired_state['bound_subject'] = params.get('bound_subject')
    desired_state['claim_mappings'] = params.get('claim_mappings')
    desired_state['groups_claim'] = params.get('groups_claim')
    desired_state['oidc_scopes'] = params.get('oidc_scopes')
    desired_state['token_bound_cidrs'] = params.get('token_bound_cidrs')
    desired_state['token_explicit_max_ttl'] = params.get('token_explicit_max_ttl')
    desired_state['token_ttl'] = params.get('token_ttl')
    desired_state['token_max_ttl'] = params.get('token_max_ttl')
    desired_state['token_no_default_policy'] = params.get('token_no_default_policy')
    desired_state['token_policies'] = params.get('token_policies')
    desired_state['policies'] = params.get('policies')
    desired_state['token_type'] = params.get('token_type')
    desired_state['user_claim'] = params.get('user_claim')
    desired_state['token_period'] = params.get('token_period')
    desired_state['token_num_uses'] = params.get('token_num_uses')
    desired_state['clock_skew_leeway'] = params.get('clock_skew_leeway')
    desired_state['expiration_leeway'] = params.get('expiration_leeway')
    desired_state['not_before_leeway'] = params.get('not_before_leeway')

    # check if role exists
    s = requests.Session()
    exists = False
    try:
        if verify:
            if ca_cert is not None:
                verify = ca_cert
            elif ca_path is not None:
                verify = ca_path
        current_state = s.get(url + '/v1/auth/' + mount_point + '/role/' + name, verify=verify, headers=headers)
        if current_state.status_code == 200:
            exists = True
    except Exception:
        changed = True

    if not exists and state == 'present':
        changed = True
    elif exists and state == 'absent':
        changed = True

    desired_state['role_type'] = "oidc"
    desired_state['verbose_oidc_logging'] = False
    if len(desired_state['token_policies']) == 0 and len(desired_state['policies']) > 0:
        desired_state['token_policies'] = desired_state['policies']
    if len(desired_state['policies']) == 0 and len(desired_state['token_policies']) > 0:
        desired_state['policies'] = desired_state['token_policies']

    # check if current role matches desired role values, if they dont match, set changed true
    if exists and state == 'present':
        current_state = current_state.json()['data']
        for k, v in desired_state.items():
            if v != current_state[k]:
                changed = True
                break

    method = None
    if changed and state == 'present' and not module.check_mode:
        method = 'POST'
    elif changed and state == 'absent' and not module.check_mode:
        method = 'DELETE'

    # make the changes!
    if method is not None:
        req = requests.Request(method, url + '/v1/auth/' + mount_point + '/role/' + name, headers=headers,
                               json=desired_state)
        prepped = s.prepare_request(req)
        resp = s.send(prepped)
        if resp.status_code not in [200, 201, 202, 204]:
            return {'failed': True, 'msg': str(resp.text), 'rc': 1}
        return {'changed': changed}
    return {'changed': changed}


if __name__ == '__main__':
    main()
