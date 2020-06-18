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
module: hashivault_policy_set
version_added: "2.1.0"
short_description: Hashicorp Vault policy set module
description:
    - Module to set a policy in Hashicorp Vault. Use hashivault_policy instead.
options:
    name:
        description:
            - policy name.
    rules:
        description:
            - policy rules.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_policy_set:
      rules: '{{rules}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['rules'] = dict(required=True, type='str')
    argspec['rules_file'] = dict(required=False, type='bool', default=False)
    module = hashivault_init(argspec)
    result = hashivault_policy_set(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_policy_set(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    rules = params.get('rules')
    rules_file = params.get('rules_file')
    if rules_file:
        try:
            rules = open(rules, 'r').read()
        except Exception as e:
            return {'changed': False, 'failed': True, 'msg': 'Error opening rules file <%s>: %s' % (rules, str(e))}
    current = client.get_policy(name)
    if current == rules:
        return {'changed': False}
    client.sys.create_or_update_policy(name, rules)
    return {'changed': True}


if __name__ == '__main__':
    main()
