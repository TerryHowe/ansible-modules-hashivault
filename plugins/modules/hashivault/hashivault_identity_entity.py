#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_identity_entity
version_added: "3.13.0"
short_description: Hashicorp Vault entity create module
description:
    - Module to manage identity entity in Hashicorp Vault.
options:
    name:
        description:
            - entity name to create or update.
    id:
        description:
            - entity id to update.
    metadata:
        description:
            - metadata to be associated with entity
    disabled:
        description:
            - whether the entity is disabled
    policies:
        description:
            - entity policies.
    state:
        description:
            - whether create/update or delete the entity
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_identity_entity:
      name: 'bob'
      policies: 'bob'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=False, type='str', default=None)
    argspec['id'] = dict(required=False, type='str', default=None)
    argspec['metadata'] = dict(required=False, type='dict', default=None)
    argspec['disabled'] = dict(required=False, type='bool', default=None)
    argspec['policies'] = dict(required=False, type='list', default=None)
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    module = hashivault_init(argspec)
    result = hashivault_identity_entity(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def hashivault_identity_entity_update(entity_details, client, entity_id, entity_name, entity_metadata, entity_disabled,
                                      entity_policies):
    if entity_metadata is None:
        entity_metadata = entity_details['metadata']
    if entity_policies is None:
        entity_policies = entity_details['policies']
    if entity_disabled is None:
        entity_disabled = entity_details['disabled']

    if entity_details['name'] != entity_name or entity_details['disabled'] != entity_disabled or \
            entity_details['metadata'] != entity_metadata or \
            set([] if entity_details['policies'] is None else entity_details['policies']) != set(entity_policies):
        try:
            client.secrets.identity.update_entity(
                entity_id=entity_id,
                name=entity_name,
                metadata=entity_metadata,
                policies=entity_policies,
                disabled=entity_disabled
            )
        except Exception as e:
            return {'failed': True, 'msg': str(e)}
        return {'changed': True}
    return {'changed': False}


def hashivault_identity_entity_create_or_update(params):
    client = hashivault_auth_client(params)
    entity_name = params.get('name')
    entity_id = params.get('id')
    entity_metadata = params.get('metadata')
    entity_disabled = params.get('disabled')
    entity_policies = params.get('policies')

    if entity_id is not None:
        try:
            entity_details = client.secrets.identity.read_entity(entity_id=entity_id)
        except Exception as e:
            return {'failed': True, 'msg': str(e)}
        return hashivault_identity_entity_update(entity_details['data'], client, entity_name, entity_id,
                                                 entity_metadata, entity_disabled, entity_policies)
    elif entity_name is not None:
        try:
            entity_details = client.secrets.identity.read_entity_by_name(name=entity_name)
        except Exception:
            response = client.secrets.identity.create_or_update_entity_by_name(
                name=entity_name,
                metadata=entity_metadata,
                policies=entity_policies,
                disabled=entity_disabled
            )
            return {'changed': True, 'data': response['data']}
        return hashivault_identity_entity_update(entity_details['data'], client, entity_name=entity_name,
                                                 entity_id=entity_details['data']['id'],
                                                 entity_metadata=entity_metadata,
                                                 entity_disabled=entity_disabled, entity_policies=entity_policies)
    return {'failed': True, 'msg': "Either name or id must be provided"}


def hashivault_identity_entity_delete(params):
    client = hashivault_auth_client(params)
    entity_id = params.get('id')
    entity_name = params.get('name')

    if entity_id is not None:
        try:
            client.secrets.identity.read_entity(entity_id=entity_id)
        except Exception:
            return {'changed': False}
        client.secrets.identity.delete_entity(entity_id=entity_id)
        return {'changed': True}
    elif entity_name is not None:
        try:
            client.secrets.identity.read_entity_by_name(name=entity_name)
        except Exception:
            return {'changed': False}
        client.secrets.identity.delete_entity_by_name(name=entity_name)
        return {'changed': True}
    return {'failed': True, 'msg': "Either name or id must be provided"}


@hashiwrapper
def hashivault_identity_entity(params):
    state = params.get('state')
    if state == 'present':
        return hashivault_identity_entity_create_or_update(params)
    elif state == 'absent':
        return hashivault_identity_entity_delete(params)
    else:
        return {'failed': True, 'msg': 'Unknown state'}


if __name__ == '__main__':
    main()
