#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_userpass
version_added: "3.12.0"
short_description: Hashicorp Vault userpass user management module
description:
    - Module to manage userpass users in Hashicorp Vault.
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
            - user name to create.
    pass:
        description:
            - user to create password.
    pass_update:
        description:
            - whether to update the password if user exists
        default: False
    policies:
        description:
            - user policies.
        default: default
    state:
        description:
            - whether create/update or delete the user
    mount_point:
        description:
            - default The "path" (app-id) the auth backend is mounted on.
        default: userpass
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_userpass_create:
      name: 'bob'
      pass: 'S3cre7s'
      policies: 'bob'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['pass'] = dict(required=False, type='str', default=None)
    argspec['pass_update'] = dict(required=False, type='bool', default=False)
    argspec['policies'] = dict(required=False, type='list', default=[])
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    argspec['mount_point'] = dict(required=False, type='str', default='userpass')
    module = hashivault_init(argspec)
    result = hashivault_userpass(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def hashivault_userpass_update(client, user_details, user_name, user_pass, user_pass_update, user_policies,
                               mount_point):
    if set(user_details['data']['policies']) != set(user_policies):
        if user_pass_update and user_pass is not None:
            client.create_userpass(user_name, user_pass, user_policies, mount_point=mount_point)
            return {'changed': True}
        else:
            client.update_userpass_policies(user_name, user_policies, mount_point=mount_point)
            return {'changed': True}
    if user_pass_update and user_pass is not None:
        client.update_userpass_password(user_name, user_pass, mount_point=mount_point)
        return {'changed': True}
    return {'changed': False}


@hashiwrapper
def hashivault_userpass(params):
    client = hashivault_auth_client(params)
    state = params.get('state')
    name = params.get('name')
    password = params.get('pass')
    password_update = params.get('pass_update')
    policies = params.get('policies')
    mount_point = params.get('mount_point')
    if state == 'present':
        try:
            user_details = client.read_userpass(name, mount_point=mount_point)
        except Exception:
            if password is not None:
                client.create_userpass(name, password, policies)
                return {'changed': True}
            else:
                return {'failed': True, 'msg': 'pass must be provided for new users'}
        else:
            return hashivault_userpass_update(client, user_details, user_name=name, user_pass=password,
                                              user_pass_update=password_update, user_policies=policies,
                                              mount_point=mount_point)
    elif state == 'absent':
        try:
            client.read_userpass(name, mount_point=mount_point)
        except Exception:
            return {'changed': False}
        else:
            client.delete_userpass(name, mount_point=mount_point)
            return {'changed': True}
    else:
        return {'failed': True, 'msg': 'Unkown state type'}


if __name__ == '__main__':
    main()
