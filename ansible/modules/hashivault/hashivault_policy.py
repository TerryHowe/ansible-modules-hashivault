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
    module = hashivault_init(argspec, mutually_exclusive=mutually_exclusive, supports_check_mode=True)
    result = hashivault_policy(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_policy(module):
    params = module.params
    client = hashivault_auth_client(params)
    state = params.get('state')
    name = params.get('name')
    exists = False
    changed = False
    current_state = {}
    desired_state = {}

    # get current policies
    current_policies = client.sys.list_policies()
    if isinstance(current_policies, dict):
        current_policies = current_policies.get('policies', current_policies)
    if name in current_policies:
        exists = True
        current_state = client.get_policy(name)

    # Define desired rules
    rules_file = params.get('rules_file')
    if rules_file:
        try:
            desired_state = open(rules_file, 'r').read()
        except Exception as e:
            return {'changed': False,
                    'failed': True,
                    'msg': 'Error opening rules file <%s>: %s' % (rules_file, str(e))}
    else:
        desired_state = params.get('rules')

    # Check required actions
    if state == 'present' and not exists:
        changed = True
    elif state == 'absent' and exists:
        changed = True
    elif state == 'present' and exists:
        if current_state != desired_state:
            changed = True

    if changed and not module.check_mode:
        # create or update
        if state == 'present':
            client.sys.create_or_update_policy(name, desired_state)
        # delete
        elif state == 'absent':
            client.sys.delete_policy(name)

    return {
        "changed": changed,
        "diff": {
            "before": current_state,
            "after": desired_state,
        },
    }


if __name__ == '__main__':
    main()
