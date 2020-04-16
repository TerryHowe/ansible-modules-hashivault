#!/usr/bin/env python

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_token_lookup
version_added: "3.3.0"
short_description: Hashicorp Vault token lookup module
description:
    - Module to look up / check for existence of tokens in Hashicorp Vault.
options:
    lookup_token:
        description:
            - token to lookup if different from auth token
        default: to authentication token
    accessor:
        description:
            - If set, lookups will use the this accessor token
    wrap_ttl:
        description:
            - Indicates that the response should be wrapped in a cubbyhole token with the requested TTL.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - name: "Lookup token"
      hashivault_token_lookup:
        lookup_token: "{{client_token}}"
      register: "vault_token_lookup"
'''


def main():
    argspec = hashivault_argspec()
    argspec['lookup_token'] = dict(required=False, type='str', no_log=True)
    argspec['accessor'] = dict(required=False, type='bool', default=False)
    argspec['wrap_ttl'] = dict(required=False, type='int')
    module = hashivault_init(argspec)
    result = hashivault_token_lookup(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_token_lookup(params):
    client = hashivault_auth_client(params)
    accessor = params.get('accessor')
    lookup_token = params.get('lookup_token')
    if lookup_token is None:
        lookup_token = params.get('token')
    wrap_ttl = params.get('wrap_ttl')
    lookup = client.lookup_token(token=lookup_token, accessor=accessor, wrap_ttl=wrap_ttl)
    return {'changed': False, 'lookup': lookup}


if __name__ == '__main__':
    main()
