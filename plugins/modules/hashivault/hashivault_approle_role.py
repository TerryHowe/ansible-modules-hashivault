#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role
version_added: "4.0.0"
short_description: Hashicorp Vault approle management role module
description:
    - Module to manage an approle role from Hashicorp Vault.
options:
    state:
        description:
            - present or absent
        default: present
    name:
        description:
            - role name.
    mount_point:
        description:
            - mount point for role
        default: approle
    bind_secret_id:
        description:
            - Require secret_id to be presented when logging in using this AppRole.
    bound_cidr_list:
        description:
            - Comma-separated string or list of CIDR blocks.
    policies:
        description:
            - policies for the role.
    secret_id_num_uses:
        description:
            - Number of times any particular SecretID can be used.
    secret_id_ttl:
        description:
            - Duration after which any SecretID expires.
    token_num_uses:
        description:
            - Number of times issued tokens can be used. A value of 0 means unlimited uses.
    token_ttl:
        description:
            - Duration to set as the TTL for issued tokens and at renewal time.
    token_max_ttl:
        description:
            - Duration after which the issued token can no longer be renewed.
    period:
        description:
            - Duration of the token generated.
    enable_local_secret_ids:
        description:
            - If set, the secret IDs generated using this role will be cluster local.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_approle_role:
        name: ashley
    - hashivault_approle_role:
        name: ashley
        state: absent
    - hashivault_approle_role:
        name: terry
        role_file: path/to/file.json
'''


def main():
    argspec = hashivault_argspec()
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    argspec['name'] = dict(required=True, type='str')
    argspec['role_file'] = dict(required=False, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='approle')
    argspec['bind_secret_id'] = dict(required=False, type='bool', no_log=True)
    argspec['bound_cidr_list'] = dict(required=False, type='list')
    argspec['policies'] = dict(required=False, type='list', default=[])
    argspec['secret_id_num_uses'] = dict(required=False, type='str')
    argspec['secret_id_ttl'] = dict(required=False, type='str')
    argspec['token_num_uses'] = dict(required=False, type='int')
    argspec['token_ttl'] = dict(required=False, type='str')
    argspec['token_max_ttl'] = dict(required=False, type='str')
    argspec['period'] = dict(required=False, type='str')
    argspec['enable_local_secret_ids'] = dict(required=False, type='bool')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_approle_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role(module):
    params = module.params
    state = params.get('state')
    role_file = params.get('role_file')
    mount_point = params.get('mount_point')
    name = params.get('name')
    client = hashivault_auth_client(params)
    if state == 'present':
        args = [
            'policies',
            'bind_secret_id',
            'bound_cidr_list',
            'secret_id_num_uses',
            'secret_id_ttl',
            'token_num_uses',
            'token_ttl',
            'token_max_ttl',
            'period',
            'enable_local_secret_ids',
        ]
        desired_state = {}
        if role_file:
            try:
                desired_state = json.loads(open(params.get('role_file'), 'r').read())
            except Exception as e:
                return {'changed': False, 'failed': True,
                        'msg': 'Error opening role file <%s>: %s' % (params.get('role_file'), str(e))}
        else:
            for arg in args:
                value = params.get(arg)
                if value is not None:
                    desired_state[arg] = value

        try:
            previous_state = client.get_role(name, mount_point=mount_point)
        except Exception:
            if not module.check_mode:
                client.create_role(name, mount_point=mount_point, **desired_state)
            return {'changed': True}

        changed = False
        missing = []
        current_data = previous_state.get('data', {})
        for key in desired_state:
            if key in current_data:
                if current_data[key] != desired_state[key]:
                    changed = True
            else:
                missing.append(key)
                changed = True
        if not changed:
            return {'changed': False, 'missing': missing, 'previous_state': previous_state}

        if not module.check_mode:
            client.create_role(name, mount_point=mount_point, **desired_state)
        return {'changed': True, 'missing': missing}
    if module.check_mode:
        try:
            client.get_role(name, mount_point=mount_point)
        except Exception:
            return {'changed': False}
        return {'changed': True}
    else:
        client.delete_role(name, mount_point=mount_point)
    return {'changed': True}


if __name__ == '__main__':
    main()
