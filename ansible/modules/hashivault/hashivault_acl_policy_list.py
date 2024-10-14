#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_acl_policy_list
version_added: "5.3.0"
short_description: Hashicorp Vault ACL policy list module
description:
    - Module to list ACL policies in Hashicorp Vault.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_acl_policy_list:
      register: 'vault_acl_policy_list'
    - debug: msg="Policies are {{vault_acl_policy_list.policy}}"
'''


def main():
    argspec = hashivault_argspec()
    module = hashivault_init(argspec)
    result = hashivault_acl_policy_list(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_acl_policy_list(params):
    client = hashivault_auth_client(params)
    current_policies = client.sys.list_acl_policies()
    if isinstance(current_policies, dict):
        current_policies = current_policies.get('data', current_policies)
        current_policies = current_policies.get('keys', current_policies)
    return {'policies': current_policies}


if __name__ == '__main__':
    main()
