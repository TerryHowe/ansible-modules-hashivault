#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_read
version_added: "0.1"
short_description: Hashicorp Vault read module
description:
    - Module to read to Hashicorp Vault.
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
            - authentication type to use: token, userpass, github, ldap
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
    secret:
        description:
            - secret to read.
        default: False
    key:
        description:
            - secret key to read.
        default: False
    register:
        description:
            - variable to register result.
        default: False
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_read:
        secret: 'giant'
        key: 'fie'
      register: 'fie'
    - debug: msg="Value is {{fie.value}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['secret'] = dict(required=True, type='str')
    argspec['key'] = dict(required=True, type='str')
    argspec['register'] = dict(required=False, type='str')
    module = hashivault_init(argspec)
    result = hashivault_read(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_read(params):
    result = { "changed": False, "rc" : 0}
    client = hashivault_auth_client(params)
    secret = params.get('secret')
    key = params.get('key')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        response = client.read('secret/%s' % secret)
        if not response:
            result['rc'] = 1
            result['failed'] = True
            result['msg'] = "Secret %s is not in vault" % secret
            return result
        data = response['data']
    if key not in data:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = "Key %s is not in secret %s" % (key, secret)
        return result
    value = data[key]
    result['value'] = value
    return result


if __name__ == '__main__':
    main()
