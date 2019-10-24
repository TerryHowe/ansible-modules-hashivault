#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json
from ast import literal_eval

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_azure_secret_engine_role
version_added: "3.17.6"
short_description: Hashicorp Vault azure secret engine role
description:
    - Module to define a Azure role that vault can generate dynamic credentials for vault
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
    mount_point:
        description:
            - name of the secret engine mount name.
        default: azure
    name:
        description:
            - name of the role in vault
    azure_role:
        description:
            - list of nested dicts filled with role content [{"role_name":"", "scope":""}]
    azure_role_file:
        description:
            - file with a single dict, azure_role
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_azure_secret_engine_role:
        name: contributor-role
        azure_role: [{ "role_name": "Contributor","scope": "/subscriptions/sub1234"}]

    - hashivault_azure_secret_engine_role:
        name: contributor-role
        azure_role_file: /users/dmullen/my-role-file.json
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['azure_role'] = dict(required=False, type='str')
    argspec['azure_role_file'] = dict(required=False, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='azure')
    supports_check_mode=True
    mutually_exclusive=[['azure_role','azure_role_file']]

    module = hashivault_init(argspec, supports_check_mode=supports_check_mode, mutually_exclusive=mutually_exclusive)
    result = hashivault_azure_secret_engine_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_azure_secret_engine_role(module):
    params = module.params
    client = hashivault_auth_client(params)
    azure_role_file = params.get('azure_role_file')
    mount_point = params.get('mount_point')
    azure_role = params.get('azure_role')
    name = params.get('name')
    changed = False

    # do not want a trailing slash in name
    if name[-1] == '/':
        name = name.strip('/')
    if mount_point[-1]:
        mount_point = mount_point.strip('/')

    # if azure_role_file is set, set azure_role to contents
    # else assume azure_role is set and use that value
    if azure_role_file:
        azure_role = json.loads(open(params.get('azure_role_file'), 'r').read())['azure_role']

    # check if engine is enabled
    try:
        if (mount_point + "/") not in client.sys.list_mounted_secrets_engines()['data'].keys():
            return {'failed': True, 'msg': 'secret engine is not enabled', 'rc': 1}
    except:
        if module.check_mode:
            changed = True
        else:
            return {'failed': True, 'msg': 'secret engine is not enabled or namespace does not exist', 'rc': 1}

    # check if role exists or any at all
    try:
        existing_roles = client.secrets.azure.list_roles(mount_point=mount_point)
        if name not in existing_roles['keys']:
            changed = True
    except:
        changed = True

    # azure_role comes from json which is assigned as a str object type, convert to py objs
    azure_role = literal_eval(azure_role)
    if not changed:
        # check if role content == desired
        current = client.secrets.aws.read_role(name=name,mount_point=mount_point)['data']['azure_roles']
        caught = 0
        for i in azure_role:
            for i2 in current:
                if i.items() <= i2.items():
                    caught = caught + 1
        if caught != len(azure_role) or caught != len(current):
            changed = True

    # make the changes!
    if changed and not module.check_mode:
        client.secrets.azure.create_or_update_role(name=name, azure_roles=azure_role)
    
    return {'changed': changed}


if __name__ == '__main__':
    main()
