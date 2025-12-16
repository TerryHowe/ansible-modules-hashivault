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
module: hashivault_radius_config
version_added: "4.7.0"
short_description: Hashicorp Vault RADIUS configuration module
description:
    - Module to configure the RADIUS authentication method in Hashicorp Vault.
options:
    mount_point:
        description:
            - location where this auth_method is mounted. also known as "path"
        default: radius
    host:
        description:
            - The RADIUS server to connect to. Examples: radius.myorg.com, 127.0.0.1
        required: True
    secret:
        description:
            - The RADIUS shared secret
        required: True
    port:
        description:
            - The UDP port where the RADIUS server is listening on. Defaults is 1812.
        default: 1812
    unregistered_user_policies:
        description:
            - A comma-separated list of policies to be granted to unregistered users.
        default: []
    dial_timeout:
        description:
            - Number of seconds to wait for a backend connection before timing out. Default is 10.
        default: 10
    nas_port:
        description:
            - The NAS-Port attribute of the RADIUS request. Defaults is 10.
        default: 10
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_radius_config:
        host: "radius.myorg.com"
        secret: "my_radius_secret"
        port: 1812
        dial_timeout: 10
        nas_port: 10
        unregistered_user_policies:
          - default
- hosts: localhost
  tasks:
    - hashivault_radius_config:
        host: "127.0.0.1"
        secret: "{{ radius_secret }}"
        mount_point: "radius"
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='radius')
    argspec['host'] = dict(required=True, type='str')
    argspec['secret'] = dict(required=True, type='str', no_log=True)
    argspec['port'] = dict(required=False, type='int', default=1812)
    argspec['unregistered_user_policies'] = dict(required=False, type='list', default=[])
    argspec['dial_timeout'] = dict(required=False, type='int', default=10)
    argspec['nas_port'] = dict(required=False, type='int', default=10)

    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_radius_config(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_radius_config(module):
    params = module.params
    client = hashivault_auth_client(params)
    changed = False
    desired_state = dict()
    desired_state['mount_point'] = params.get('mount_point')
    desired_state['host'] = params.get('host')
    desired_state['secret'] = params.get('secret')
    desired_state['port'] = params.get('port')
    desired_state['unregistered_user_policies'] = params.get('unregistered_user_policies')
    desired_state['dial_timeout'] = params.get('dial_timeout')
    desired_state['nas_port'] = params.get('nas_port')

    # if secret is None, remove it from desired state since we can't compare
    if desired_state['secret'] is None:
        del desired_state['secret']

    # check current config
    current_state = dict()
    try:
        result = client.auth.radius.read_configuration(
            mount_point=desired_state['mount_point'])['data']
        # map keys from Vault response to desired state keys
        current_state['host'] = result.get('host', '')
        current_state['port'] = result.get('port', 1812)
        current_state['unregistered_user_policies'] = result.get('unregistered_user_policies', [])
        current_state['dial_timeout'] = result.get('dial_timeout', 10)
        current_state['nas_port'] = result.get('nas_port', 10)
    except InvalidPath:
        pass

    # If no current config exists, we need to configure
    if not current_state:
        changed = True
    else:
        # check if current config matches desired config values, if they match, set changed to false to prevent action
        for k, v in current_state.items():
            if k in desired_state and v != desired_state[k]:
                changed = True
                break

    # if configs dont match and checkmode is off, complete the change
    if changed and not module.check_mode:
        client.auth.radius.configure(**desired_state)

    return {'changed': changed}


if __name__ == '__main__':
    main()
