#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_token_create
version_added: "2.2.0"
short_description: Hashicorp Vault token create module
description:
    - Module to create tokens in Hashicorp Vault.
options:
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    verify:
        description:
            - verify TLS certificate
        default: to environment variable VAULT_SKIP_VERIFY
    authtype:
        description:
            - "authentication type to use: token, userpass, github, ldap"
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
        default: False
    password:
        description:
            - password to login to vault.
        default: False
    name:
        description:
            - user name to create.
        default: False
    pass:
        description:
            - user to create password.
        default: False
    policies:
        description:
            - user policies.
        default: default
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_token_create:
      policies: ['stan', 'kyle']
      lease: '1h'
      orphan: yes
      renewable: yes 
      token: {{ 
'''


def main():
    argspec = hashivault_argspec()
    argspec['role'] = dict(required=False, type='str')
    argspec['id'] = dict(required=False, type='str')
    argspec['policies'] = dict(required=True, type='list')
    argspec['metadata'] = dict(required=False, type='str')
    argspec['no_parent'] = dict(required=False, type='str')
    argspec['lease'] = dict(required=False, type='str')
    argspec['display_name'] = dict(required=True, type='str')
    argspec['num_uses'] = dict(required=False, type='str')
    argspec['no_default_policy'] = dict(required=False, type='bool', default=False)
    argspec['ttl'] = dict(required=False, type='str')
    argspec['wrap_ttl'] = dict(required=False, type='str')
    argspec['orphan'] = dict(required=False, type='bool', default=False)
    argspec['renewable'] = dict(required=False, type='bool')
    argspec['explicit_max_ttl'] = dict(required=False, type='str')
    module = hashivault_init(argspec)
    result = hashivault_token_create(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_token_create(params):
    client = hashivault_auth_client(params)
    role = params.get('role')
    id = params.get('id')
    policies = params.get('policies')
    metadata = params.get('metadata')
    no_parent = params.get('no_parent')
    lease = params.get('lease')
    display_name = params.get('display_name')
    num_uses = params.get('num_uses')
    no_default_policy = params.get('no_default_policy')
    ttl = params.get('ttl')
    wrap_ttl = params.get('wrap_ttl')
    orphan = params.get('orphan')
    renewable = params.get('renewable')
    explicit_max_ttl = params.get('explicit_max_ttl')

    token = client.create_token(
        role=role,
        id=id,
        policies=policies,
        meta=metadata,
        no_parent=no_parent,
        lease=lease,
        display_name=display_name,
        num_uses=num_uses,
        no_default_policy=no_default_policy,
        ttl=ttl,
        wrap_ttl=wrap_ttl,
        orphan=orphan,
        renewable=renewable,
        explicit_max_ttl=explicit_max_ttl
        )

    return {'changed': True, 'token': token}

if __name__ == '__main__':
    main()
