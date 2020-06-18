#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['deprecated'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_policy_set_from_file
version_added: "2.1.0"
short_description: Hashicorp Vault policy set from a file module
description:
    - Module to set a policy from a file in Hashicorp Vault. Use hashivault_policy_set instead.
options:
    name:
        description:
            - policy name.
    rules_file:
        description:
            - policy rules file.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_policy_set_from_file:
      rules_file: /path/to/policy_file.hcl
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['rules_file'] = dict(required=True, type='str')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_policy_set_from_file(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_policy_set_from_file(module):
    params = module.params
    client = hashivault_auth_client(params)
    name = params.get('name')
    rules = open(params.get('rules_file'), 'r').read()
    changed = False
    exists = False
    current = str()

    # does policy exit
    try:
        current = client.get_policy(name)
        exists = True
    except Exception:
        if module.check_mode:
            changed = True
        else:
            return {'failed': True, 'msg': 'auth mount is not enabled', 'rc': 1}

    # does current policy match desired
    if exists:
        if current != rules:
            changed = True

    if exists and changed and not module.check_mode:
        client.sys.create_or_update_policy(name, rules)

    return {'changed': changed}


if __name__ == '__main__':
    main()
