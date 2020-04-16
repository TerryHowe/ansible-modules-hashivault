#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_token_renew
version_added: "3.11.0"
short_description: Hashicorp Vault token renew module
description:
    - Module to renew tokens in Hashicorp Vault.
options:
    renew_token:
        description:
            - token to renew if different from auth token
        default: to authentication token
    increment:
        description:
            - "Request a specific increment for renewal. Vault is not required to honor this request. If not supplied,\
             Vault will use the default TTL."
    wrap_ttl:
        description:
            - Indicates that the response should be wrapped in a cubbyhole token with the requested TTL.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - name: "Renew token"
      hashivault_token_renew:
        renew_token: "{{client_token}}"
        increment: "5m"
      register: "vault_token_renew"
'''


def main():
    argspec = hashivault_argspec()
    argspec['renew_token'] = dict(required=False, type='str', no_log=True)
    argspec['increment'] = dict(required=False, type='str', default=None)
    argspec['wrap_ttl'] = dict(required=False, type='int')
    module = hashivault_init(argspec)
    result = hashivault_token_renew(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_token_renew(params):
    client = hashivault_auth_client(params)
    renew_token = params.get('renew_token')
    increment = params.get('increment')
    if renew_token is None:
        renew_token = params.get('token')
    wrap_ttl = params.get('wrap_ttl')
    renew = client.renew_token(token=renew_token, increment=increment, wrap_ttl=wrap_ttl)
    return {'changed': True, 'renew': renew}


if __name__ == '__main__':
    main()
