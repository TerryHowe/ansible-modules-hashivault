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
module: hashivault_k8s_auth_role
version_added: "4.3.1"
short_description: Hashicorp Vault kubernetes secret engine role
description:
    - Module to define a kubernetes role that vault can generate dynamic credentials for vault
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
        default: kubernetes
    name:
        description:
            - name of the role in vault
    ttl:
        description:
            - TTL period of tokens issued using this role in seconds
    max_ttl:
        description:
            - maximum allowed lifetime of tokens issued in seconds using this role.
    policies:
        description:
            - policies to be set on tokens issued using this role.
    period:
        description:
            - If set, indicates that the token generated using this role should never expire. The token should
              be renewed within the duration specified by this value. At each renewal, the token's TTL will be set
              to the value of this parameter
    role_file:
        description:
            - File with a json object containing play parameters. pass all params but name, state, mount_point which
              stay in the ansible play


'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_k8s_auth_role:
        name: "test"
        policies: ["test", "test2"]
        bound_service_account_names: ["vault-auth"]
        bound_service_account_namespaces: ["default", "some-app"]

    - hashivault_k8s_auth_role:
        name: test
        role_file: some_k8s_role.json
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['bound_service_account_names'] = dict(required=False, type='list', default=[])
    argspec['bound_service_account_namespaces'] = dict(required=False, type='list', default=[])
    argspec['ttl'] = dict(required=False, type='int', default=0)
    argspec['max_ttl'] = dict(required=False, type='int', default=0)
    argspec['policies'] = dict(required=False, type='list')
    argspec['period'] = dict(required=False, type='int', default=0)
    argspec['mount_point'] = dict(required=False, type='str', default='kubernetes')
    argspec['role_file'] = dict(required=False, type='str')
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_k8s_auth_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_k8s_auth_role(module):
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

    if role_file:
        desired_state = json.loads(open(params.get('role_file'), 'r').read())
    else:
        desired_state['bound_service_account_names'] = params.get('bound_service_account_names')
        desired_state['bound_service_account_namespaces'] = params.get('bound_service_account_namespaces')
        desired_state['ttl'] = params.get('ttl')
        desired_state['max_ttl'] = params.get('max_ttl')
        desired_state['period'] = params.get('period')
        desired_state['policies'] = params.get('policies')

    # check if engine is enabled
    try:
        if (mount_point + "/") not in client.sys.list_auth_methods():
            return {'failed': True, 'msg': 'auth method is not enabled', 'rc': 1}
    except:
        if module.check_mode:
            changed = True
        else:
            return {'failed': True, 'msg': 'auth mount is not enabled or namespace does not exist', 'rc': 1}

    # check if role exists
    try:
        existing_roles = client.auth.kubernetes.list_roles(mount_point=mount_point)
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
        current_state = client.auth.kubernetes.read_role(name=name, mount_point=mount_point)
        # Map a couple elements
        if 'ttl' not in current_state and 'token_ttl' in current_state:
            current_state['ttl'] = current_state['token_ttl']
        if 'max_ttl' not in current_state and 'token_max_ttl' in current_state:
            current_state['max_ttl'] = current_state['token_max_ttl']
        if 'period' not in current_state and 'token_period' in current_state:
            current_state['period'] = current_state['token_period']
        for key in desired_state.keys():
            if key in current_state and desired_state[key] != current_state[key]:
                changed = True
    elif exists and state == 'absent':
        changed = True

    if changed and state == 'present' and not module.check_mode:
        client.auth.kubernetes.create_role(name=name, mount_point=mount_point, **desired_state)

    elif changed and state == 'absent' and not module.check_mode:
        client.auth.kubernetes.delete_role(name=name, mount_point=mount_point)

    return {'changed': changed}


if __name__ == '__main__':
    main()
