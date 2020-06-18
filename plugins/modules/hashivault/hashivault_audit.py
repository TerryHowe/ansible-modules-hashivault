#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_audit
version_added: "2.2.0"
short_description: Hashicorp Vault audit module
description:
    - Module to enable/disable audit backends in Hashicorp Vault.
options:
    device_type:
        description:
            - device_type of auditor
    path:
        description:
            - path of auditor
        default: value of device_type
    description:
        description:
            - description of auditor
    options:
        description:
            - options for auditor
    state:
        description:
            - should auth mount be enabled or disabled
        default: enabled
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_audit:
        device_type: syslog
'''


def main():
    argspec = hashivault_argspec()
    argspec['device_type'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str', default='')
    argspec['options'] = dict(required=False, type='dict')
    argspec['path'] = dict(required=False, type='str')
    argspec['state'] = dict(required=False, type='str', default='enabled',
                            choices=['enabled', 'enable', 'present', 'disabled', 'disable', 'absent'])
    module = hashivault_init(argspec)
    result = hashivault_audit(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_audit(params):
    client = hashivault_auth_client(params)
    device_type = params.get('device_type')
    description = params.get('description')
    options = params.get('options')
    path = params.get('path')
    state = params.get('state')
    if state in ['enabled', 'enable', 'present']:
        state = 'enabled'
    else:
        state = 'disabled'

    result = client.sys.list_enabled_audit_devices()
    backends = result.get('data', result)
    if not path:
        path = device_type + "/"
    if path[-1] != "/":
        path = path + "/"

    if state == 'enabled':
        if path in backends:
            return {'changed': False, 'msg': 'Backend exists and Vault does not support update'}
        client.sys.enable_audit_device(device_type=device_type, description=description, options=options, path=path)
    elif state == 'disabled':
        if path not in backends:
            return {'changed': False, 'msg': 'Backend does not exist'}
        client.sys.disable_audit_device(path=path)
    return {'changed': True}


if __name__ == '__main__':
    main()
