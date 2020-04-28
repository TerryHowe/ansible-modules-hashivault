#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_ldap_group
version_added: "3.18.3"
short_description: Hashicorp Vault LDAP group configuration module
description:
    - Module to configure LDAP groups in Hashicorp Vault.
options:
    mount_point:
        description:
            - location where this method/backend is mounted. also known as "path"
        default: ldap
    name:
        description:
            - name of the group
        default: None
    policies:
        description:
            - policies to be tied to the group
        default: None
    state:
        description:
            - whether create/update or delete the entity
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_ldap_group:
        name: 'my-group'
        policies:
            - 'my-policy'
        token: "{{ vault_token }}"
        url: "{{ vault_url }}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str', default=None)
    argspec['mount_point'] = dict(required=False, type='str', default='ldap')
    argspec['policies'] = dict(required=False, type='list', default=[])
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    module = hashivault_init(argspec)
    result = hashivault_ldap_group(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def hashivault_ldap_group_update(group_details, client, group_name, group_policies, mount_point):
    changed = False

    # existing policies
    if group_details['policies'] is not None:
        if set(group_details['policies']) != set(group_policies):
            changed = True
    # new policies and none existing
    elif len(group_policies) > 0:
        changed = True

    if changed:
        try:
            response = client.auth.ldap.create_or_update_group(
                name=group_name,
                policies=group_policies,
                mount_point=mount_point
            )
        except Exception as e:
            return {'failed': True, 'msg': str(e)}
        if response.status_code == 204:
            return {'changed': True}
        return {'changed': True, 'data': response}
    return {'changed': False}


def hashivault_ldap_group_create_or_update(params):
    client = hashivault_auth_client(params)
    group_name = params.get('name')
    mount_point = params.get('mount_point')
    group_policies = params.get('policies')
    try:
        group_details = client.auth.ldap.read_group(name=group_name, mount_point=mount_point)
    except Exception:
        client.auth.ldap.create_or_update_group(
            name=group_name,
            policies=group_policies,
            mount_point=mount_point
        )
        return {'changed': True}
    return hashivault_ldap_group_update(group_details['data'], client, group_name=group_name,
                                        group_policies=group_policies,
                                        mount_point=mount_point)


def hashivault_ldap_group_delete(params):
    client = hashivault_auth_client(params)
    group_name = params.get('name')

    try:
        client.auth.ldap.read_group(name=group_name)
    except Exception:
        return {'changed': False}
    client.auth.ldap.delete_group(name=group_name)
    return {'changed': True}


@hashiwrapper
def hashivault_ldap_group(params):
    state = params.get('state')
    if state == 'present':
        return hashivault_ldap_group_create_or_update(params)
    elif state == 'absent':
        return hashivault_ldap_group_delete(params)


if __name__ == '__main__':
    main()
