#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
from hvac.exceptions import InvalidPath

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_acl_policy_get
version_added: "5.3.0"
short_description: Hashicorp Vault ACL policy get module
description:
    - Module to get an ACL policy from Hashicorp Vault.
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
    - hashivault_acl_policy_get:
      name: 'annie'
      register: 'vault_acl_policy_get'
    - debug: msg="User policy is {{vault_acl_policy_get.policy}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_acl_policy_get(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_acl_policy_get(params):
    name = params.get('name')
    client = hashivault_auth_client(params)
    try:
        policy = client.sys.read_acl_policy(name)
        policy = policy.get('data', policy).get('policy', policy)
    except InvalidPath as e:
        policy = None

    if policy is None:
        result = {"changed": False, "rc": 1, "failed": True}
        result['msg'] = u"Policy \"%s\" does not exist." % name
        return result
    else:
        return {'rules': policy}


if __name__ == '__main__':
    main()
