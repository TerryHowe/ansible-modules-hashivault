#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_namespace
version_added: "4.0.1"
short_description: Hashicorp Vault create / delete namespaces
description:
    - Module to create or delete Hashicorp Vault namespaces (enterprise only)
options:
    name:
        description:
            - name of the namespace
    state:
        description:
            - state of secret backend. choices: present, disabled
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_namespace:
        name: teama

    - name: "create a child namespace 'team1' in 'teama' ns: teama/team1"
      hashivault_namespace:
        name: team1
        namespace: teama
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['state'] = dict(required=False, type='str', choices=['present', 'absent'], default='present')
    module = hashivault_init(argspec)
    result = hashivault_secret_engine(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_secret_engine(module):
    params = module.params
    client = hashivault_auth_client(params)
    name = params.get('name')
    state = params.get('state')
    current_state = dict()
    exists = False
    changed = False

    try:
        # does the ns exist already?
        current_state = client.sys.list_namespaces()['data']['keys']
        if (name + '/') in current_state:
            exists = True
    except Exception:
        # doesnt exist
        pass

    # doesnt exist and should or does exist and shouldnt
    if (exists and state == 'absent') or (not exists and state == 'present'):
        changed = True

    # create
    if changed and not exists and state == 'present' and not module.check_mode:
        client.sys.create_namespace(path=name)

    # delete
    elif changed and (state == 'absent' or state == 'disabled') and not module.check_mode:
        client.sys.delete_namespace(path=name)

    return {'changed': changed}


if __name__ == '__main__':
    main()
