#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

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
        name: nested_ns_role
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
    argspec['role_type'] = dict(required=False, type='str', default='oidc', choices=['oidc', 'jwt'])

    module = hashivault_init(argspec)
    result = hashivault_oidc_auth_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_oidc_auth_role(module):
    params = module.params
    mount_point = params.get('mount_point').strip('/')
    name = params.get('name').strip('/')
    state = params.get('state')
    client = hashivault_auth_client(params)
    parameters = [
        'allowed_redirect_uris',
        'bound_audiences',
        'bound_claims',
        'bound_subject',
        'claim_mappings',
        'groups_claim',
        'oidc_scopes',
        'token_bound_cidrs',
        'token_explicit_max_ttl',
        'token_ttl',
        'token_max_ttl',
        'token_no_default_policy',
        'token_policies',
        'policies',
        'token_type',
        'user_claim',
        'token_period',
        'token_num_uses',
        'clock_skew_leeway',
        'expiration_leeway',
        'not_before_leeway',
        'role_type',
    ]
    desired_state = dict()
    for parameter in parameters:
        if params.get(parameter) is not None:
            desired_state[parameter] = params.get(parameter)
    desired_state['verbose_oidc_logging'] = False
    if not desired_state['token_policies'] and desired_state['policies']:
        desired_state['token_policies'] = desired_state['policies']
    desired_state.pop('policies', None)
    desired_state['path'] = mount_point

    changed = False
    current_state = {}
    try:
        current_state = client.auth.oidc.read_role(name=name, path=mount_point)['data']
    except Exception:
        changed = True
    for key in desired_state.keys():
        current_value = current_state.get(key, None)
        if current_value is not None and current_value != desired_state[key]:
            changed = True
            break

    if changed and not module.check_mode:
        if not current_state and state == 'present':
            client.auth.oidc.create_role(name=name, **desired_state)
        elif current_state and state == 'absent':
            client.auth.oidc.delete_role(name=name)
    return {'changed': changed, 'old_state': current_state, 'new_state': desired_state}


if __name__ == '__main__':
    main()
