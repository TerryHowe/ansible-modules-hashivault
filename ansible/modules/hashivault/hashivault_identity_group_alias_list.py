#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_identity_group_alias_list
version_added: "4.7.1"
short_description: Hashicorp Vault group alias list
description:
    - Module to list group aliases from Hashicorp Vault.
options:
    mount_point:
        description:
            - mount point for identity secrets engine
        default: identity
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_identity_group_alias_list:
      register: 'vault_group_alias_list'
    - debug: msg="Group Aliases are {{vault_group_alias_list.keys}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='identity')
    argspec['method'] = dict(required=False, type='str', default='GET')
    module = hashivault_init(argspec)
    result = hashivault_identity_group_alias_list(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_identity_group_alias_list(params):
    client = hashivault_auth_client(params)
    result = client.secrets.identity.list_group_aliases(
            mount_point=params.get('mount_point'),
            method=params.get('method').upper())
    if isinstance(result, dict):
        result = result.get('data', result)
    return {'changed': False, 'group_aliases': result}


if __name__ == '__main__':
    main()
