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
short_description: Hashicorp Vault ldap configuration module
description:
    - Module to configure the LDAP authentication method in Hashicorp Vault.
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
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_ldap_configure:
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

DEFAULT_MOUNT_POINT = 'identity'
DEFAULT_GROUP_TYPE = 'internal'

def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=False, type='str', default=None)
    argspec['id'] = dict(required=False, type='str', default=None)
    argspec['group_type'] = dict(required=False, type='str', default=None)
    argspec['mount_point'] = dict(required=False, type='str', default=None)
    argspec['metadata'] = dict(required=False, type='dict', default=None)
    argspec['policies'] = dict(required=False, type='list', default=None)
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
    set_member_group_ids = False

    if group_metadata is None:
        group_metadata = group_details['metadata']
    if group_policies is None:
        group_policies = group_details['policies']

    if group_member_group_ids is None:
        group_member_group_ids = group_details['member_group_ids']

    if group_member_entity_ids is None:
        group_member_entity_ids = group_details['member_entity_ids']

    # new member group id's and existing id's
    if group_member_group_ids is not None and group_details['member_group_ids'] is not None:
        if set(group_details['member_group_ids']) != set(group_member_group_ids):
            set_member_group_ids = True
    # new member group id's and none existing
    elif group_member_group_ids is not None:
        set_member_group_ids = True

    if group_details['name'] != group_name or \
        group_details['type'] != group_type or \
        group_details['metadata'] != group_metadata or \
        set(group_details['policies']) != set(group_policies) or \
        set(group_details['member_entity_ids']) != set(group_member_entity_ids) or \
        set_member_group_ids:
        try:
            client.secrets.identity.update_group(
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
        return {'changed': True}
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
    
    if mount_point is None:
        mount_point = DEFAULT_MOUNT_POINT
    
    if group_type is None:
        group_type = DEFAULT_GROUP_TYPE

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
            return {'changed': True, 'data': response.json()['data']}
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
    else:
        return {'failed': True, 'msg': 'Unknown state'}


if __name__ == '__main__':
    main()
