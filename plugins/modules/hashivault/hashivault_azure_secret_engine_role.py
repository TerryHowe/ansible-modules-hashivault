#!/usr/bin/env python
from ansible.module_utils.hashivault import check_secrets_engines
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json
from ast import literal_eval

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_azure_secret_engine_role
version_added: "3.17.6"
short_description: Hashicorp Vault azure secret engine role
description:
    - Module to define a Azure role that vault can generate dynamic credentials for vault
options:
    mount_point:
        description:
            - name of the secret engine mount name.
        default: azure
    name:
        description:
            - name of the role in vault
    azure_role:
        description:
            - list of nested dicts filled with role content [{"role_name":"", "scope":""}]
    azure_role_file:
        description:
            - file with a single dict, azure_role
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_azure_secret_engine_role:
        name: contributor-role
        azure_role: [{ "role_name": "Contributor","scope": "/subscriptions/sub1234"}]

    - hashivault_azure_secret_engine_role:
        name: contributor-role
        azure_role_file: /users/dmullen/my-role-file.json
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['azure_role'] = dict(required=False, type='str')
    argspec['azure_role_file'] = dict(required=False, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='azure')
    mutually_exclusive = [['azure_role', 'azure_role_file']]

    module = hashivault_init(argspec, supports_check_mode=True, mutually_exclusive=mutually_exclusive)
    result = hashivault_azure_secret_engine_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_azure_secret_engine_role(module):
    params = module.params
    client = hashivault_auth_client(params)
    azure_role_file = params.get('azure_role_file')
    mount_point = params.get('mount_point').strip('/')
    azure_role = params.get('azure_role')
    name = params.get('name').strip('/')
    changed = False

    # if azure_role_file is set, set azure_role to contents
    # else assume azure_role is set and use that value
    if azure_role_file:
        azure_role = json.loads(open(params.get('azure_role_file'), 'r').read())['azure_role']

    # check if engine is enabled
    changed, err = check_secrets_engines(module, client)
    if err:
        return err

    # check if role exists or any at all
    try:
        existing_roles = client.secrets.azure.list_roles(mount_point=mount_point)
        if name not in existing_roles['keys']:
            changed = True
    except Exception:
        changed = True

    # azure_role comes from json which is assigned as a str object type, convert to py objs
    azure_role = literal_eval(azure_role)
    if not changed:
        # check if role content == desired
        current = client.secrets.aws.read_role(name=name, mount_point=mount_point)['data']['azure_roles']
        caught = 0
        for i in azure_role:
            for i2 in current:
                if i.items() <= i2.items():
                    caught = caught + 1
        if caught != len(azure_role) or caught != len(current):
            changed = True

    # make the changes!
    if changed and not module.check_mode:
        client.secrets.azure.create_or_update_role(name=name, azure_roles=azure_role)

    return {'changed': changed}


if __name__ == '__main__':
    main()
