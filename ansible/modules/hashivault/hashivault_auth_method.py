#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible.module_utils.hashivault import is_state_changed
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_auth_method
version_added: "3.17.7"
short_description: Hashicorp Vault auth module
description:
    - Module to enable or disable authentication methods in Hashicorp Vault.
options:
    method_type:
        description:
            - name of auth method. [required]
    description:
        description:
            - description of authenticator
    mount_point:
        description:
            - location where this auth_method will be mounted. also known as "path"
    state:
        description:
            - should auth mount be enabled or disabled
        default: enabled
    config:
        description:
            - configuration set on auth method. expects a dict
        default: "{'default_lease_ttl': 2764800, 'max_lease_ttl': 2764800, 'force_no_cache':False,
                  'token_type': 'default-service'}"
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_auth_method:
        method_type: userpass
'''

RETURN = r'''
path:
    description: The path of the auth method.
    type: str
    returned: always
result:
    description: The current configuration of the auth method if it exists.
    type: dict
    returned: always
'''

DEFAULT_TTL = 2764800
DEFAULT_CONFIG = {
    'default_lease_ttl': DEFAULT_TTL,
    'max_lease_ttl': DEFAULT_TTL,
    'force_no_cache': False,
    'token_type': 'default-service'
}


def main():
    argspec = hashivault_argspec()
    argspec['method_type'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str', default='')
    argspec['state'] = dict(required=False, type='str', default='enabled',
                            choices=['enabled', 'disabled', 'enable', 'disable'])
    argspec['mount_point'] = dict(required=False, type='str', default=None)
    argspec['config'] = dict(required=False, type='dict',
                             default=DEFAULT_CONFIG)
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_auth_method(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_auth_method(module):
    params = module.params
    client = hashivault_auth_client(params)
    method_type = params.get('method_type')
    description = params.get('description')
    mount_point = params.get('mount_point')
    config = params.get('config')
    if params.get('state') in ['enabled', 'enable']:
        state = 'enabled'
    else:
        state = 'disabled'
    exists = False
    changed = False
    create = False
    current_state = {}
    desired_state = {
        'config': config,
        'description': description
    }

    if mount_point is None:
        mount_point = method_type

    # Get current auth methods
    try:
        result = client.sys.list_auth_methods()
        auth_methods = result.get('data', result)
        if (mount_point + u"/") in auth_methods:
            exists = True
    except Exception:
        pass

    # Check required actions
    if state == 'enabled' and not exists:
        changed = True
        create = True
    elif state == 'disabled' and exists:
        changed = True
    elif exists and state == 'enabled':
        auth_method = auth_methods[mount_point + u"/"]
        current_state = {
            'config': auth_method['config'],
            'description': auth_method['description']
        }
        changed = description != auth_method['description'] or is_state_changed(config, auth_method['config'])

    # create
    if state == 'enabled' and changed and not module.check_mode:
        if create:
            client.sys.enable_auth_method(method_type, description=description, path=mount_point, config=config)
        # update
        else:
            client.sys.tune_auth_method(description=description, path=mount_point, **config)
    # delete
    elif state == 'disabled' and changed and not module.check_mode:
        client.sys.disable_auth_method(path=mount_point)

    # Get resulting auth method
    try:
        final_result = client.sys.list_auth_methods()
        retval = final_result['data'][mount_point + u"/"]
    except Exception:
        retval = {}
        pass

    return {
        "changed": changed,
        "created": create,
        "path": mount_point,
        "result": retval,
        "diff": {
            "before": current_state,
            "after": desired_state,
        },
    }


if __name__ == '__main__':
    main()
