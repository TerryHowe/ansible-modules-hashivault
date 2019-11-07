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
        default: "{'default_lease_ttl': 2764800, 'max_lease_ttl': 2764800, 'force_no_cache':False, 'token_type': 'default-service'}"
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_method:
        method_type: userpass
'''

DEFAULT_TTL = 2764800

def main():
    argspec = hashivault_argspec()
    argspec['method_type'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    argspec['state'] = dict(required=False, type='str', default='enabled', choices=['enabled','disabled','enable','disable'])
    argspec['mount_point'] = dict(required=False, type='str', default=None)
    argspec['config'] = dict(required=False, type='dict', default={'default_lease_ttl':DEFAULT_TTL, 'max_lease_ttl':DEFAULT_TTL, 'force_no_cache':False, 'token_type': 'default-service'})
    supports_check_mode = True
    module = hashivault_init(argspec, supports_check_mode=supports_check_mode)
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
    created = False

    if mount_point == None:
        mount_point = method_type

    try:
        auth_methods = client.sys.list_auth_methods()
        path = (mount_point or method_type) + u"/"

        # Is auth method enabled already?
        if path in auth_methods['data'].keys():
            exists = True
    except:
        if module.check_mode:
            changed = True

    # if its off and we want it on
    if (state == 'enabled' or state == 'enable') and exists == False:
        changed = True
    # if its on and we want it off
    elif (state == 'disabled' or state == 'disable') and exists == True:
        changed = True

    # its on, we want it on, need to check current config vs desired
    if not changed and exists and (state == 'enabled' or state == 'enable'):
        current_state = client.sys.read_auth_method_tuning(path=mount_point)
        if 'default_lease_ttl' not in config:
            config['default_lease_ttl'] = DEFAULT_TTL
        if 'max_lease_ttl' not in config:
            config['max_lease_ttl'] = DEFAULT_TTL
        if 'force_no_cache' not in config:
            config['force_no_cache'] = False
        if 'token_type' not in config:
            config['token_type'] = 'default-service'
        if current_state['data'] != config:
            changed = True

    # brand new
    if changed and not exists and not module.check_mode and (state == 'enabled' or state == 'enable'):
        client.sys.enable_auth_method(method_type, description=description, path=mount_point, config=config)
        created = True
    # delete existing
    if changed and not module.check_mode and (state == 'disabled' or state == 'disable'):
        client.sys.disable_auth_method(path=mount_point)
    # update existing
    if changed and exists and not module.check_mode and (state == 'enabled' or state == 'enable'):
        client.sys.tune_auth_method(description=description, path=mount_point, **config)
    return {'changed': changed, 'created': created}

if __name__ == '__main__':
    main()
