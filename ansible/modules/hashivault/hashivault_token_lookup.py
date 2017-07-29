
#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_token_lookup
version_added: "3.3.0"
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
    password:
        description:
            - password to login to vault.
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
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
      hashivault_token_lookup:
        lookup_token: "{{client_token}}"
      register: "vault_token_lookup"
'''


def main():
    argspec = hashivault_argspec()
    argspec['lookup_token'] = dict(required=False, type='str')
    argspec['accessor'] = dict(required=False, type='bool', default=False)
    argspec['wrap_ttl'] = dict(required=False, type='int')
    module = hashivault_init(argspec)
    result = hashivault_token_lookup(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


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
