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
    secret:
        description:
            - secret to read.
    key:
        description:
            - secret key to read.
    register:
        description:
            - variable to register result.
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
    argspec['key'] = dict(required=False, type='str')
    argspec['register'] = dict(required=False, type='str')
    argspec['default'] = dict(required=False, default=None, type='str')
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
    default = params.get('default')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if secret.startswith('/'):
            secret = secret.lstrip('/')
            response = client.read(secret)
        else:
            response = client.read(u'secret/%s' % secret)
        if not response:
            if default is not None:
                result['value'] = default
                return result
            result['rc'] = 1
            result['failed'] = True
            result['msg'] = u"Secret %s is not in vault" % secret
            return result
        data = response['data']
    if key and key not in data:
        if default is not None:
            result['value'] = default
            return result
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Key %s is not in secret %s" % (key, secret)
        return result
    if key:
        value = data[key]
    else:
        value = data
    result['value'] = value
    return result


if __name__ == '__main__':
    main()
