#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_token_revoke
version_added: "3.11.0"
short_description: Hashicorp Vault token revoke module
description:
    - Module to revoke tokens in Hashicorp Vault.
options:
    revoke_token:
        description:
            - token to revoke if different from auth token
        default: to authentication token
    accessor:
        description:
            - If set, lookups will use the this accessor token
    orphan:
        description:
            - If set, Vault will revoke only the token, leaving the children as orphans.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - name: "revoke token"
      hashivault_token_revoke:
        revoke_token: "{{client_token}}"
      register: "vault_token_revoke"
'''


def main():
    argspec = hashivault_argspec()
    argspec['revoke_token'] = dict(required=False, type='str')
    argspec['accessor'] = dict(required=False, type='bool', default=False)
    argspec['orphan'] = dict(required=False, type='bool', default=False)
    module = hashivault_init(argspec)
    result = hashivault_token_revoke(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_token_revoke(params):
    client = hashivault_auth_client(params)
    accessor = params.get('accessor')
    orphan = params.get('orphan')
    revoke_token = params.get('revoke_token')
    if revoke_token is None:
        revoke_token = params.get('token')
    revoke = client.revoke_token(token=revoke_token, orphan=orphan, accessor=accessor)
    return {'changed': True, 'revoke': revoke}


if __name__ == '__main__':
    main()
