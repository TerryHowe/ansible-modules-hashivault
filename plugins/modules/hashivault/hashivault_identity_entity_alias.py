#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_identity_entity_alias
version_added: "3.13.0"
short_description: Hashicorp Vault entity alias manage module
description:
    - Module to manage identity entity aliases in Hashicorp Vault.
options:
    name:
        description:
            - Name of the alias. Name should be the identifier of the client in the authentication source.
    alias_id:
        description:
            - ID of the entity alias. If set, updates the  corresponding entity alias.
    entity_name:
        description:
            - Entity name to which this alias belongs to.
    canonical_id:
        description:
            - Entity ID to which this alias belongs to.
    mount_accessor:
        description:
            - Accessor of the mount to which the alias should belong to.
    state:
        description:
            - whether crete/update or delete the entity
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_identity_entity_alias:
      name: 'bob'
      entity_name: 'bob'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str', default=None)
    argspec['alias_id'] = dict(required=False, type='str', default=None)
    argspec['entity_name'] = dict(required=False, type='str', default=None)
    argspec['canonical_id'] = dict(required=False, type='str', default=None)
    argspec['mount_accessor'] = dict(required=False, type='str', default=None)
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    module = hashivault_init(argspec)
    result = hashivault_identity_entity_alias(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def hashivault_identity_entity_alias_update(client, alias_id, alias_name, canonical_id, mount_accessor):
    try:
        alias_details = client.secrets.identity.read_entity_alias(alias_id=alias_id)
    except Exception as e:
        return {'failed': True, 'msg': str(e)}
    if alias_details['data']['canonical_id'] == canonical_id:
        return {'changed': False}
    try:
        client.secrets.identity.update_entity_alias(
            alias_id=alias_id,
            name=alias_name,
            canonical_id=canonical_id,
            mount_accessor=mount_accessor
        )
    except Exception as e:
        return {'failed': True, 'msg': str(e)}
    return {'changed': True}


def hashivault_identity_entity_alias_create(client, alias_name, canonical_id, mount_accessor):
    try:
        list_of_aliases = client.secrets.identity.list_entity_aliases()
    except Exception:
        try:
            alias_details = client.secrets.identity.create_or_update_entity_alias(
                name=alias_name,
                canonical_id=canonical_id,
                mount_accessor=mount_accessor
            )
        except Exception as e:
            return {'failed': True, 'msg': str(e)}
        return {'changed': True, 'data': alias_details['data']}
    for key, value in dict(list_of_aliases['data']['key_info']).items():
        if value['mount_accessor'] == mount_accessor and value['name'] == alias_name:
            return hashivault_identity_entity_alias_update(client, alias_id=key, alias_name=alias_name,
                                                           canonical_id=canonical_id,
                                                           mount_accessor=mount_accessor)
    else:
        try:
            client.secrets.identity.create_or_update_entity_alias(name=alias_name, canonical_id=canonical_id,
                                                                  mount_accessor=mount_accessor)
        except Exception as e:
            return {'failed': True, 'msg': str(e)}
        return {'changed': True}


def hashivault_identity_entity_alias_delete(client, alias_id, alias_name, mount_accessor, canonical_id):
    try:
        list_of_aliases = client.secrets.identity.list_entity_aliases()
    except Exception:
        return {'changed': False}
    else:
        if alias_id is not None:
            if alias_id not in list_of_aliases['data']['keys']:
                return {'changed': False}
            client.secrets.identity.delete_entity_alias(alias_id=alias_id)
            return {'changed': True}
        elif alias_name is not None:
            for key, value in dict(list_of_aliases['data']['key_info']).items():
                if value['mount_accessor'] == mount_accessor and \
                        value['name'] == alias_name and \
                        value['canonical_id'] == canonical_id:
                    client.secrets.identity.delete_entity_alias(alias_id=key)
                    return {'changed': True}
            return {'changed': False}
        return {'failed': True, 'msg': 'Either alias_id or name must be provided'}


@hashiwrapper
def hashivault_identity_entity_alias(params):
    client = hashivault_auth_client(params)
    alias_name = params.get('name')
    alias_id = params.get('alias_id')
    state = params.get('state')
    mount_accessor = params.get('mount_accessor')
    authtype = params.get('authtype')
    entity_name = params.get('entity_name')
    canonical_id = params.get('canonical_id')

    # Get mount_accessor if not provided
    if mount_accessor is None:
        auth_method_details = client.read(path="/sys/auth/")
        try:
            mount_accessor = auth_method_details['data'][authtype + "/"]['accessor']
        except Exception:
            return {'failed': True, 'msg': 'Auth method %s not found. Use mount_accessor?' % authtype}

    # Get canonical_id if not provided
    if canonical_id is None:
        if entity_name is None:
            return {'failed': True, 'msg': 'Either canonical_id or entity_name must be provided'}
        else:
            try:
                entity_details = client.secrets.identity.read_entity_by_name(
                    name=entity_name
                )
            except Exception:
                return {'failed': True, 'msg': 'No entity with name %s' % entity_name}
            canonical_id = entity_details['data']['id']

    if state == 'present':
        if alias_id is not None:
            return hashivault_identity_entity_alias_update(client, alias_id=alias_id, alias_name=alias_name,
                                                           mount_accessor=mount_accessor, canonical_id=canonical_id)
        elif alias_name is not None:
            return hashivault_identity_entity_alias_create(client, alias_name=alias_name, mount_accessor=mount_accessor,
                                                           canonical_id=canonical_id)
        else:
            return {'failed': True, 'msg': 'Either alias_id or name must be provided'}
    elif state == 'absent':
        return hashivault_identity_entity_alias_delete(client, alias_id=alias_id, alias_name=alias_name,
                                                       mount_accessor=mount_accessor, canonical_id=canonical_id)
    return {'failed': True, 'msg': 'Unknown state'}


if __name__ == '__main__':
    main()
