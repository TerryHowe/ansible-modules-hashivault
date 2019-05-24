#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_auth_method
version_added: "3.17.7"
short_description: Hashicorp Vault auth module
description:
    - Module to enable or disable authentication ethods in Hashicorp Vault.
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
    method_type:
        description:
            - name of auth method. [required]
    description:
        description:
            - description of authenticator
    mount_point:
        description:
            - location where this auth_method will be mounted. also known as "path"
    state:
        description:
            - should auth mount be enabled or disabled
        default: enabled
    config:
        description:
            - configuration set on auth method. expects a dict
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_method:
        method_type: userpass
'''


def main():
    argspec = hashivault_argspec()
    argspec['method_type'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    argspec['state'] = dict(required=False, type='str', default='enabled', choices=['enabled','disabled','enable','disable'])
    argspec['mount_point'] = dict(required=False, type='str', default=None)
    argspec['config'] = dict(required=False, type='dict', default=None)
    module = hashivault_init(argspec)
    result = hashivault_auth_method(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_auth_method(module):
    params = module.params
    client = hashivault_auth_client(params)
    method_type = params.get('method_type')
    description = params.get('description')
    mount_point = params.get('mount_point')
    config = params.get('config')
    state = params.get('state')
    exists = False
    changed = False

    if mount_point == None:
        mount_point = method_type

    auth_methods = client.sys.list_auth_methods()
    path = (mount_point or method_type) + u"/"

    # is auth method enabled already?
    if path in auth_methods['data'].keys():
        exists = True

    # if its off and we want it on
    if (state == 'enabled' or state == 'enable') and exists == False:
        changed = True
    # if its on and we want it off
    elif (state == 'disabled' or state == 'disable') and exists == True:
        changed = True

    if changed and not module.check_mode and (state == 'enabled' or state == 'enable'):
        client.sys.enable_auth_method(method_type, description=description, path=mount_point, config=config)

    if changed and not module.check_mode and (state == 'disabled' or state == 'disable'):
        client.sys.disable_auth_method(path=mount_point)

    return {'changed': changed}

if __name__ == '__main__':
    main()
