#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_policy_set
version_added: "2.1.0"
short_description: Hashicorp Vault policy set module
description:
    - Module to set a policy in Hashicorp Vault.
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
            - "path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate : if ca_cert is specified, its value will take precedence"
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
            - "if set, do not verify presented TLS certificate before communicating with Vault server : setting this variable is not recommended except during testing"
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
    name:
        description:
            - policy name.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_policy_set:
      rules: '{{rules}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['rules'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_policy_set(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_policy_set(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    rules = params.get('rules')
    current = client.get_policy(name)
    if current == rules:
        return {'changed': False}
    client.set_policy(name, rules)
    return {'changed': True}


if __name__ == '__main__':
    main()
