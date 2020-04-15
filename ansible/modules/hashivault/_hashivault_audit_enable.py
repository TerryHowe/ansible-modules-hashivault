#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['deprecated'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_audit_enable
version_added: "2.2.0"
short_description: Hashicorp Vault audit enable module
description:
    - Module to enable audit backends in Hashicorp Vault. Use hashivault_audit instead.
options:
    name:
        description:
            - name of auditor
    description:
        description:
            - description of auditor
    options:
        description:
            - options for auditor
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_audit_enable:
        name: "syslog"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['description'] = dict(required=False, type='str')
    argspec['options'] = dict(required=False, type='dict')
    module = hashivault_init(argspec)
    result = hashivault_audit_enable(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_audit_enable(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    description = params.get('description')
    options = params.get('options')
    backends = client.sys.list_enabled_audit_devices()
    backends = backends.get('data', backends)
    path = name + "/"
    if path in backends and backends[path]["options"] == options:
        return {'changed': False}
    client.sys.enable_audit_device(name, description=description, options=options)
    return {'changed': True}


if __name__ == '__main__':
    main()
