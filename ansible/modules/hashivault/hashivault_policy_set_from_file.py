#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_policy_set_from_file
version_added: "2.1.0"
short_description: Hashicorp Vault policy set from a file module
description:
    - Module to set a policy from a file in Hashicorp Vault.
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
    name:
        description:
            - policy name.
    rules_file:
        description:
            - policy rules file.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_policy_set_from_file:
      rules_file: /path/to/policy_file.hcl
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['rules_file'] = dict(required=True, type='str')
    supports_check_mode = True
    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_policy_set_from_file(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_policy_set_from_file(module):
    params = module.params
    client = hashivault_auth_client(params)
    name = params.get('name')
    rules = open(params.get('rules_file'), 'r').read()
    changed = False
    exists = False
    current = str()

    # does policy exit
    try:
        current = client.get_policy(name)
        exists = True
    except:
        if module.check_mode:
            changed = True
        else:
            return {'failed': True, 'msg': 'auth mount is not enabled', 'rc': 1}

    # does current policy match desired
    if exists:
        if current != rules:
            changed = True

    if exists and changed and not module.check_mode:
        client.sys.create_or_update_policy(name, rules)

    return {'changed': changed}


if __name__ == '__main__':
    main()
