#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_k8s_auth_role
version_added: "4.3.1"
short_description: Hashicorp Vault kubernetes secret engine role
description:
    - Module to define a kubernetes role that vault can generate dynamic credentials for vault
options:
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
extends_documentation_fragment: hashivault
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

    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_k8s_auth_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_k8s_auth_role(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point').strip('/')
    role_file = params.get('role_file')
    name = params.get('name').strip('/')
    state = params.get('state')
    desired_state = dict()
    exists = False
    changed = False

    if role_file:
        desired_state = json.loads(open(params.get('role_file'), 'r').read())
    else:
        desired_state['bound_service_account_names'] = params.get('bound_service_account_names')
        desired_state['bound_service_account_namespaces'] = params.get('bound_service_account_namespaces')
        desired_state['ttl'] = params.get('ttl')
        desired_state['max_ttl'] = params.get('max_ttl')
        desired_state['period'] = params.get('period')
        desired_state['policies'] = params.get('policies')

    # check if role exists
    try:
        existing_roles = client.auth.kubernetes.list_roles(mount_point=mount_point)
        if name in existing_roles['keys']:
            # this role exists
            exists = True
    except Exception:
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
