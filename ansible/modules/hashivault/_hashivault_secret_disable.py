#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['deprecated'], 'alternative': 'Use M(hashivault_secret_engine) instead.',
                    'why': 'This module does not fit the standard pattern',
                    'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_secret_disable
version_added: "2.2.0"
short_description: Hashicorp Vault secret disable module
description:
    - Module to disable secret backends in Hashicorp Vault. Use hashivault_secret_engine instead.
options:
    name:
        description:
            - name of secret backend
    backend:
        description:
            - type of secret backend
    description:
        description:
            - description of secret backend
    config:
        description:
            - config of secret backend
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_secret_disable:
        name: "ephemeral"
        backend: "generic"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_secret_disable(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_secret_disable(params):
    client = hashivault_auth_client(params)
    name = params.get('name')
    client.sys.disable_secrets_engine(name)
    return {'changed': True}


if __name__ == '__main__':
    main()
