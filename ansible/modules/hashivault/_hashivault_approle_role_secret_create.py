#!/usr/bin/env python

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['deprecated'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role_secret_create
version_added: "3.8.0"
short_description: Hashicorp Vault approle role secret id create module
description:
    - Module to get an approle role secret id from Hashicorp Vault in Pull mode
      or create custom approle role secret id in Push mode. Use hashivault_approle_role_secret instead.
options:
    name:
        description:
            - secret name.
    secret_id:
        description:
            - Custom SecretID to be attached to the role.
    cidr_list:
        description:
            - Comma-separated string or list of CIDR blocks.
    metadata:
        description:
            - Metadata to be tied to the secret.
    wrap_ttl:
        description:
            - Wrap TTL.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_approle_role_secret_create:
        name: 'ashley'
      register: 'vault_approle_role_secret_create'
    - debug: msg="Role secret id is {{vault_approle_role_secret_create.id}}"

- hosts: localhost
  tasks:
    - hashivault_approle_role_secret_create:
        name: 'robert'
        secret_id: '{{ lookup("password", "/dev/null length=32 chars=ascii_letters,digits") }}'
      register: 'vault_approle_role_custom_secret_create'
    - debug: msg="Role custom secret id is {{vault_approle_role_custom_secret_create.id}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['secret_id'] = dict(required=False, type='str')
    argspec['cidr_list'] = dict(required=False, type='str')
    argspec['metadata'] = dict(required=False, type='dict')
    argspec['wrap_ttl'] = dict(required=False, type='str')
    module = hashivault_init(argspec)
    result = hashivault_approle_role_secret_create(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role_secret_create(params):
    name = params.get('name')
    custom_secret_id = params.get('secret_id')
    cidr_list = params.get('cidr_list')
    metadata = params.get('metadata')
    wrap_ttl = params.get('wrap_ttl')

    client = hashivault_auth_client(params)

    if custom_secret_id is not None:
        result = client.create_role_custom_secret_id(role_name=name,
                                                     secret_id=custom_secret_id,
                                                     meta=metadata)
    else:
        result = client.create_role_secret_id(role_name=name, meta=metadata,
                                              cidr_list=cidr_list,
                                              wrap_ttl=wrap_ttl)
    return result['data']


if __name__ == '__main__':
    main()
