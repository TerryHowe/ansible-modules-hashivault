#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_identity_group
version_added: "3.17.7"
short_description: Hashicorp Vault identity group configuration module
description:
    - Module to configure identity groups in Hashicorp Vault.
options:
    mount_point:
        description:
            - location where this method/backend is mounted. also known as "path"
        default: identity
    name:
        description:
            - name of the group
        default: None
    id:
        description:
            - ID of the group
        default: None
    group_type:
        description:
            - Type of the group, internal or external. Defaults to internal
        default: internal
    metadata:
        description:
            - metadata to be associated with the group
        default: None
    policies:
        description:
            - policies to be tied to the group
        default: None
    member_group_ids:
        description:
            - group IDs to be assigned as group members
        default: None
    member_entity_ids:
        description:
            - entity IDs to be assigned as group members
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
    - hashivault_identity_group:
        name: 'my-group'
        policies:
            - 'my-policy'
        member_group_ids:
            - 'group-id-xxxx'
        member_entity_ids:
            - 'entity-id-xxxx'
        metadata:
            'department': 'ops'
        token: "{{ vault_token }}"
        url: "{{ vault_url }}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=False, type='str', default=None)
    argspec['id'] = dict(required=False, type='str', default=None)
    argspec['group_type'] = dict(required=False, type='str', default='internal')
    argspec['mount_point'] = dict(required=False, type='str', default='identity')
    argspec['metadata'] = dict(required=False, type='dict', default={})
    argspec['policies'] = dict(required=False, type='list', default=[])
    argspec['member_group_ids'] = dict(required=False, type='list', default=None)
    argspec['member_entity_ids'] = dict(required=False, type='list', default=None)
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    module = hashivault_init(argspec)
    result = hashivault_identity_group(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def hashivault_identity_group_update(group_details, client, group_id, group_name, group_type, group_metadata,
                                     group_policies, group_member_group_ids, group_member_entity_ids, mount_point):
    changed = False

    # if the groups were created without any entity members, group members, or policies,
    # then vault will return null for each respectively
    # if they were created with these and then all were removed it returns an empty list
    # for each respectively. The below is required to account for this
    # existing member_group_ids
    if group_details['member_group_ids'] is not None and group_member_group_ids is not None:
        if set(group_details['member_group_ids']) != set(group_member_group_ids):
            changed = True
    # new member_group_ids and none existing
    elif group_member_group_ids is not None and len(group_member_group_ids) > 0:
        changed = True

    # existing policies
    if group_details['policies'] is not None:
        if set(group_details['policies']) != set(group_policies):
            changed = True
    # new policies and none existing
    elif len(group_policies) > 0:
        changed = True

    # existing member_entity_ids
    if group_details['member_entity_ids'] is not None and group_member_entity_ids is not None:
        if set(group_details['member_entity_ids']) != set(group_member_entity_ids):
            changed = True
    # new member_entity_ids and none existing
    elif group_member_entity_ids is not None and len(group_member_entity_ids) > 0:
        changed = True

    # existing metadata
    if group_details['metadata'] is not None:
        if group_details['metadata'] != group_metadata:
            changed = True
    # new metadata and none existing
    elif len(group_metadata) > 0:
        changed = True

    if group_details['name'] != group_name or group_details['type'] != group_type or changed:
        try:
            response = client.secrets.identity.update_group(
                group_id=group_id,
                name=group_name,
                group_type=group_type,
                metadata=group_metadata,
                policies=group_policies,
                member_group_ids=group_member_group_ids,
                member_entity_ids=group_member_entity_ids,
                mount_point=mount_point
            )
        except Exception as e:
            return {'failed': True, 'msg': str(e)}
        if response.status_code == 204:
            return {'changed': True}
        return {'changed': True, 'data': response}
    return {'changed': False}


def hashivault_identity_group_create_or_update(params):
    client = hashivault_auth_client(params)
    group_name = params.get('name')
    group_id = params.get('id')
    group_type = params.get('group_type')
    mount_point = params.get('mount_point')
    group_metadata = params.get('metadata')
    group_policies = params.get('policies')
    group_member_group_ids = params.get('member_group_ids')
    group_member_entity_ids = params.get('member_entity_ids')

    if group_id is not None:
        try:
            group_details = client.secrets.identity.read_group(group_id=group_id)
        except Exception as e:
            return {'failed': True, 'msg': str(e)}
        return hashivault_identity_group_update(group_details['data'], client, group_id, group_name, group_type,
                                                group_metadata, group_policies, group_member_group_ids,
                                                group_member_entity_ids, mount_point)
    elif group_name is not None:
        try:
            group_details = client.secrets.identity.read_group_by_name(name=group_name)
        except Exception:
            response = client.secrets.identity.create_or_update_group_by_name(
                name=group_name,
                group_type=group_type,
                metadata=group_metadata,
                policies=group_policies,
                member_group_ids=group_member_group_ids,
                member_entity_ids=group_member_entity_ids,
                mount_point=mount_point
            )
            from requests.models import Response
            if isinstance(response, Response):
                response = response.json()
            return {'changed': True, 'data': response['data']}
        return hashivault_identity_group_update(group_details['data'], client, group_name=group_name,
                                                group_id=group_details['data']['id'],
                                                group_type=group_type,
                                                group_metadata=group_metadata,
                                                group_policies=group_policies,
                                                group_member_group_ids=group_member_group_ids,
                                                group_member_entity_ids=group_member_entity_ids,
                                                mount_point=mount_point)
    return {'failed': True, 'msg': "Either name or id must be provided"}


def hashivault_identity_group_delete(params):
    client = hashivault_auth_client(params)
    group_id = params.get('id')
    group_name = params.get('name')

    if group_id is not None:
        try:
            client.secrets.identity.read_group(group_id=group_id)
        except Exception:
            return {'changed': False}
        client.secrets.identity.delete_group(group_id=group_id)
        return {'changed': True}
    elif group_name is not None:
        try:
            client.secrets.identity.read_group_by_name(name=group_name)
        except Exception:
            return {'changed': False}
        client.secrets.identity.delete_group_by_name(name=group_name)
        return {'changed': True}
    return {'failed': True, 'msg': "Either name or id must be provided"}


@hashiwrapper
def hashivault_identity_group(params):
    state = params.get('state')
    if state == 'present':
        return hashivault_identity_group_create_or_update(params)
    elif state == 'absent':
        return hashivault_identity_group_delete(params)


if __name__ == '__main__':
    main()
