#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_write
version_added: "0.1"
short_description: Hashicorp Vault write module
description:
    - Module to write to Hashicorp Vault.
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
    data:
        description:
            - Keys and values to write.
    update:
        description:
            - Update rather than overwrite.
        default: False
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_write:
        secret: giant
        data:
            foo: foe
            fie: fum
'''


def main():
    argspec = hashivault_argspec()
    argspec['secret'] = dict(required=True, type='str')
    argspec['update'] = dict(required=False, default=False, type='bool')
    argspec['data'] = dict(required=False, default={}, type='dict')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_write(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_write(module):
    result = {"changed": False, "rc": 0}
    params = module.params
    client = hashivault_auth_client(params)
    secret = params.get('secret')
    returned_data = None
    
    if secret.startswith('/'):
        secret = secret.lstrip('/')
    else:
        secret = ('secret/%s' % secret)
    data = params.get('data')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        changed = True
        write_data = data

        changed = True
        if params.get('update') or module.check_mode:
            # Do not move this read outside of the update
            read_data = client.read(secret) or {}
            read_data = read_data.get('data', {})

            write_data = dict(read_data)
            write_data.update(data)

            result['write_data'] = write_data
            result['read_data'] = read_data
            changed = write_data != read_data

        if changed:
            if not module.check_mode:
                returned_data = client.write((secret), **write_data)

            if returned_data:
                result['data'] = returned_data
            result['msg'] = "Secret %s written" % secret
        result['changed'] = changed
    return result


if __name__ == '__main__':
    main()
