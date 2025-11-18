#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_radius_user
version_added: "4.7.0"
short_description: Hashicorp Vault RADIUS user management module
description:
    - Module to manage RADIUS users in Hashicorp Vault.
options:
    name:
        description:
            - username to create/update/delete
        required: True
    policies:
        description:
            - List of policies associated with the user
        default: []
    state:
        description:
            - whether to create/update or delete the user
        choices: ['present', 'absent']
        default: present
    mount_point:
        description:
            - The "path" the auth backend is mounted on
        default: radius
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_radius_user:
        name: 'bob'
        policies:
          - 'default'
          - 'bob-policy'
- hosts: localhost
  tasks:
    - hashivault_radius_user:
        name: 'alice'
        policies:
          - 'alice-policy'
        state: present
- hosts: localhost
  tasks:
    - hashivault_radius_user:
        name: 'old-user'
        state: absent
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['policies'] = dict(required=False, type='list', default=[])
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    argspec['mount_point'] = dict(required=False, type='str', default='radius')
    module = hashivault_init(argspec)
    result = hashivault_radius_user(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def hashivault_radius_user_update(user_details, client, user_name, user_policies, mount_point):
    changed = False

    # existing policies
    if user_details['policies'] is not None:
        if set(user_details['policies']) != set(user_policies):
            changed = True
    # new policies and none existing
    elif len(user_policies) > 0:
        changed = True

    if changed:
        try:
            response = client.auth.radius.register_user(
                username=user_name,
                policies=user_policies,
                mount_point=mount_point
            )
        except Exception as e:
            return {'failed': True, 'msg': str(e)}
        if response.status_code == 204:
            return {'changed': True}
        return {'changed': True, 'data': response}
    return {'changed': False}


def hashivault_radius_user_create_or_update(params):
    client = hashivault_auth_client(params)
    user_name = params.get('name')
    mount_point = params.get('mount_point')
    user_policies = params.get('policies')
    try:
        user_details = client.auth.radius.read_user(username=user_name, mount_point=mount_point)
    except Exception:
        client.auth.radius.register_user(
            username=user_name,
            policies=user_policies,
            mount_point=mount_point
        )
        return {'changed': True}
    return hashivault_radius_user_update(user_details['data'], client, user_name=user_name,
                                         user_policies=user_policies,
                                         mount_point=mount_point)


def hashivault_radius_user_delete(params):
    client = hashivault_auth_client(params)
    user_name = params.get('name')
    mount_point = params.get('mount_point')

    try:
        client.auth.radius.read_user(username=user_name, mount_point=mount_point)
    except Exception:
        return {'changed': False}
    client.auth.radius.delete_user(username=user_name, mount_point=mount_point)
    return {'changed': True}


@hashiwrapper
def hashivault_radius_user(params):
    state = params.get('state')
    if state == 'present':
        return hashivault_radius_user_create_or_update(params)
    elif state == 'absent':
        return hashivault_radius_user_delete(params)


if __name__ == '__main__':
    main()
