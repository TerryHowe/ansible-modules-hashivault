#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_policy_get
version_added: "2.1.0"
short_description: Hashicorp Vault policy get module
description:
    - Module to get a policy from Hashicorp Vault.
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
    - hashivault_policy_get:
      name: 'annie'
      register: 'vault_policy_get'
    - debug: msg="User policy is {{vault_policy_get.policy}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_policy_get(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_policy_get(params):
    name = params.get('name')
    client = hashivault_auth_client(params)
    policy = client.get_policy(name)
    if policy is None:
        result = {"changed": False, "rc": 1, "failed": True}
        result['msg'] = u"Policy \"%s\" does not exist." % name
        return result
    else:
        return {'rules': policy}


if __name__ == '__main__':
    main()
