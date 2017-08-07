#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_read
version_added: "3.4.2"
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
            - file to read.
    dest:
        description:
            - file dest.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_read:
        secret: 'giant'
        file: 'foo.dat'
        dest: '/tmp/foo.dat'
        overwrite: false
'''


def main():
    argspec = hashivault_argspec()
    argspec['secret'] = dict(required=True, type='str')
    argspec['file'] = dict(required=True, type='str')
    argspec['dest'] = dict(required=True, type='str')
    argspec['overwrite'] = dict(required=False, default=False, type='bool')
    module = hashivault_init(argspec)
    result = hashivault_read(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *
import os.path


@hashiwrapper
def hashivault_read(params):
    result = { "changed": False, "rc" : 0}
    client = hashivault_auth_client(params)
    secret = params.get('secret')
    filename = params.get('file')
    dest = params.get('dest')
    overwrite = params.get('overwrite')

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if secret.startswith('/'):
            secret = secret.lstrip('/')
            response = client.read(secret)
        else:
            response = client.read('secret/%s' % secret)
        if not response:
            result['rc'] = 1
            result['failed'] = True
            result['msg'] = "Secret %s is not in vault" % secret
            return result
        data = response['data']

    if filename not in data:
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = "File %s is not in secret %s" % (filename, secret)
        return result

    if not overwrite and os.path.exists(dest):
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = "File %s already exists" % (dest)
        return result

    with open(dest,'w+') as f:
        f.write(data[filename].decode('base64'))

    result["changed"] = True
    return result

if __name__ == '__main__':
    main()