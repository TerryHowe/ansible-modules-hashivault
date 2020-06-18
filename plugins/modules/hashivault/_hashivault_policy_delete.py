#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['deprecated'], 'alternative': 'Use M(hashivault_policy) instead.',
                    'why': 'This module does not fit the standard pattern',
                    'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_policy_delete
version_added: "2.1.0"
short_description: Hashicorp Vault policy delete module
description:
    - Module to delete a policy from Hashicorp Vault. Use hashivault_policy instead.
options:
    name:
        description:
            - policy name.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_policy_delete:
        name: 'annie'
      register: 'vault_policy_delete'
    - debug: msg="User policy is {{vault_policy_delete.policy}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_policy_delete(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_policy_delete(params):
    name = params.get('name')
    client = hashivault_auth_client(params)
    current_policies = client.sys.list_policies()
    if isinstance(current_policies, dict):
        current_policies = current_policies.get('data', current_policies)
        current_policies = current_policies.get('policies', current_policies)
    if name not in current_policies:
        return {'changed': False}
    client.sys.delete_policy(name)
    return {'changed': True}


if __name__ == '__main__':
    main()
