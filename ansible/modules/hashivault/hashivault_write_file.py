#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_write_file
version_added: "3.4.2"
short_description: Hashicorp Vault write file module
description:
    - Module to write a file to Hashicorp Vault. Takes care of base64 encoding.
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
    secret:
        description:
            - secret to read.
    file:
        description:
            - dest file name
    path:
        description:
            - path of file to write
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_write_file:
        secret: giant
        file: foo.dat
        path: /tmp/foo.dat
'''


def main():
    argspec = hashivault_argspec()
    argspec['secret'] = dict(required=True, type='str')
    argspec['file'] = dict(required=True, type='str')
    argspec['path'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_write_file(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_write_file(params):
    result = { "changed": False, "rc" : 0}
    client = hashivault_auth_client(params)
    secret = params.get('secret')
    filename = params.get('file')

    if secret.startswith('/'):
        secret = secret.lstrip('/')
    else:
        secret = ('secret/%s' % secret)

    with open(params.get('path')) as f:
        data = {filename: f.read().encode('base64')}

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        returned_data = client.write((secret), **data)
        if returned_data:
            result['data'] = returned_data
            result['msg'] = "Secret %s written" % secret

    result['changed'] = True
    return result

if __name__ == '__main__':
    main()