#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_policy
version_added: "2.1.0"
short_description: Hashicorp Vault policy set module
description:
    - Module to set a policy in Hashicorp Vault. Use hashivault_policy instead.
options:
    name:
        description:
            - policy name.
    state:
        type: str
        choices: ["present", "absent"]
        default: present
        description:
            - present or absent
    rules:
        description:
            - policy rules.
    rules_file:
        description:
            - name of local file to read for policy rules.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_policy:
        name: my_policy
        rules: '{{rules}}'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['rules'] = dict(required=False, type='str')
    argspec['rules_file'] = dict(required=False, type='str')
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    mutually_exclusive = [['rules', 'rules_file']]
    module = hashivault_init(argspec, mutually_exclusive=mutually_exclusive)
    result = hashivault_policy(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_policy(params):
    client = hashivault_auth_client(params)
    state = params.get('state')
    name = params.get('name')
    if state == 'present':
        rules_file = params.get('rules_file')
        if rules_file:
            try:
                rules = open(rules_file, 'r').read()
            except Exception as e:
                return {'changed': False,
                        'failed': True,
                        'msg': 'Error opening rules file <%s>: %s' % (rules_file, str(e))}
        else:
            rules = params.get('rules')
        current = client.get_policy(name)
        if current == rules:
            return {'changed': False}
        client.sys.create_or_update_policy(name, rules)
        return {'changed': True}

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
