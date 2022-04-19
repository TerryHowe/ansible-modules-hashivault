#!/usr/bin/env python
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

    if mount_point is None:
        mount_point = method_type

    try:
        result = client.sys.list_auth_methods()
        auth_methods = result.get('data', result)
        if (mount_point + u"/") in auth_methods:
            exists = True
    except Exception:
        pass

    if state == 'enabled' and not exists:
        changed = True
        create = True
    elif state == 'disabled' and exists:
        changed = True
    elif exists and state == 'enabled':
        current_state = auth_methods[mount_point + u"/"]
        changed = description != current_state['description'] or is_state_changed(config, current_state['config'])

    if module.check_mode:
        return {'changed': changed, 'created': create, 'state': state}
    if not changed:
        return {'changed': changed, 'created': False, 'state': state}

    if state == 'enabled':
        if create:
            client.sys.enable_auth_method(method_type, description=description, path=mount_point, config=config)
        else:
            client.sys.tune_auth_method(description=description, path=mount_point, **config)
    if state == 'disabled':
        client.sys.disable_auth_method(path=mount_point)

    return {'changed': changed, 'created': create}


if __name__ == '__main__':
    main()
