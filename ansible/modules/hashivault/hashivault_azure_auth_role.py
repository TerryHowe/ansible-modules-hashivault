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
module: hashivault_azure_auth_role
version_added: "3.17.7"
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
    policies:
        description:
            - name of policies in vault to assign to role
    token_ttl:
        description:
            - The TTL period of tokens issued using this role in seconds.
    token_max_ttl:
        description:
            - The maximum allowed lifetime of tokens issued in seconds using this role.
    token_period:
        description:
            - If set, indicates that the token generated using this role should never expire. The token should be renewed within the duration specified by this value. At each renewal, the token's TTL will be set to the value of this parameter.
    bound_service_principal_ids:
        description:
            - The list of Service Principal IDs that login is restricted to.
    bound_group_ids:
        description:
            - The list of group ids that login is restricted to.
    bound_locations:
        description:
            - The list of locations that login is restricted to.
    bound_subscription_ids:
        description:
            - The list of subscription IDs that login is restricted to.
    bound_resource_groups:
        description:
            - The list of resource groups that login is restricted to.
    bound_scale_sets:
        description:
            - The list of scale set names that the login is restricted to.
    role_file:
        description:
            - file with a json object containing play parameters. pass all params but name, state, mount_point which stay in the ansible play
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_azure_auth_role:
        name: "test"
        policies: ["test"]
        bound_subscription_ids: ["6a1d5988-5917-4221-b224-904cd7e24a25"]
        num_uses: 3

    - hashivault_azure_auth_role:
        name: test
        role_file: /users/drewbuntu/my-auth-role.json
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['role_file'] = dict(required=False, type='str')
    argspec['policies'] = dict(required=False, type='list')
    argspec['mount_point'] = dict(required=False, type='str', default='azure')
    argspec['token_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_max_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_period'] = dict(required=False, type='int', default=0)
    argspec['bound_service_principal_ids'] = dict(required=False, type='list', default=[])
    argspec['bound_group_ids'] = dict(required=False, type='list', default=[])
    argspec['bound_locations'] = dict(required=False, type='list', default=[])
    argspec['bound_subscription_ids'] = dict(required=False, type='list', default=[])
    argspec['bound_resource_groups'] = dict(required=False, type='list', default=[])
    argspec['bound_scale_sets'] = dict(required=False, type='list', default=[])
    argspec['num_uses'] = dict(required=False, type='int', default=0)

    supports_check_mode=True

    module = hashivault_init(argspec, supports_check_mode) #, required_one_of)
    result = hashivault_azure_auth_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_azure_auth_role(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point')
    role_file = params.get('role_file')
    name = params.get('name')
    state = params.get('state')
    desired_state = dict()
    exists = False
    changed = False

    # do not want a trailing slash in name
    if name[-1] == '/':
        name = name.strip('/')
    if mount_point[-1]:
        mount_point = mount_point.strip('/')

    # if azure_role_file is set, set azure_role to contents
    # else assume azure_role is set and use that value
    if role_file:
        desired_state = json.loads(open(params.get('role_file'), 'r').read())
    else:
        desired_state['policies'] = params.get('policies')
        desired_state['ttl'] = params.get('token_ttl')
        desired_state['max_ttl'] = params.get('token_max_ttl')
        desired_state['period'] = params.get('token_period')
        desired_state['bound_service_principal_ids'] = params.get('bound_service_principal_ids')
        desired_state['bound_group_ids'] = params.get('bound_group_ids')
        desired_state['bound_locations'] = params.get('bound_locations')
        desired_state['bound_subscription_ids'] = params.get('bound_subscription_ids')
        desired_state['bound_resource_groups'] = params.get('bound_resource_groups')
        desired_state['bound_scale_sets'] = params.get('bound_scale_sets')
        desired_state['num_uses'] = params.get('num_uses')


    # check if engine is enabled
    try:
        if (mount_point + "/") not in client.sys.list_auth_methods()['data'].keys():
            return {'failed': True, 'msg': 'auth method is not enabled', 'rc': 1}
    except:
        if module.check_mode:
            changed = True
        else:
            return {'failed': True, 'msg': 'auth mount is not enabled or namespace does not exist', 'rc': 1}

    # check if role exists
    try:
        existing_roles = client.auth.azure.list_roles(mount_point=mount_point)
        if name in existing_roles['keys']:
            # this role exists
            exists = True
    except:
        # no roles exist yet
        pass

    if not exists and state == 'present':
        changed = True

    # compare current_state to desired_state
    if exists and state == 'present' and not changed:
        current_state = client.auth.azure.read_role(name=name)
        # Map a couple elements
        if 'ttl' not in current_state and 'token_ttl' in current_state:
            current_state['ttl'] = current_state['token_ttl']
        if 'max_ttl' not in current_state and 'token_max_ttl' in current_state:
            current_state['max_ttl'] = current_state['token_max_ttl']
        if 'period' not in current_state and 'token_period' in current_state:
            current_state['period'] = current_state['token_period']
        for k, v in desired_state.items():
            if k in current_state and v != current_state[k]:
                changed = True
    elif exists and state == 'absent':
        changed = True
    
    # make the changes!
    # NOTE: bound_location is paseed. will need to be changed eventually
    # https://github.com/hvac/hvac/issues/451
    if changed and state == 'present' and not module.check_mode:
        client.auth.azure.create_role(name=name, mount_point=mount_point, **desired_state)
    
    elif changed and state == 'absent' and not module.check_mode:
        client.auth.azure.delete_role(name=name, mount_point=mount_point)

    return {'changed': changed}


if __name__ == '__main__':
    main()
