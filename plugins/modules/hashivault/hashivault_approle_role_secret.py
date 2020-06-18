#!/usr/bin/env python

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_approle_role_secret
version_added: "4.0.0"
short_description: Hashicorp Vault approle role secret id manager
description:
    - Create, update and delete approle secrets.
options:
    state:
        description:
            - present or absent
        default: present
    name:
        description:
            - secret name.
    mount_point:
        description:
            - mount point for role
        default: approle
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
    secret:
        description:
            - secret id for delete.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_approle_role_secret:
        name: ashley
        state: present
      register: vault_approle_role_secret_create
    - debug: msg="Role secret id is {{vault_approle_role_secret_create.id}}"

- hosts: localhost
  tasks:
    - hashivault_approle_role_secret:
        name: robert
        state: present
        secret_id: '{{ lookup("password", "/dev/null length=32 chars=ascii_letters,digits") }}'
      register: vault_approle_role_custom_secret_create
    - debug: msg="Role custom secret id is {{vault_approle_role_custom_secret_create.id}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='approle')
    argspec['secret_id'] = dict(required=False, type='str')
    argspec['cidr_list'] = dict(required=False, type='str')
    argspec['metadata'] = dict(required=False, type='dict')
    argspec['wrap_ttl'] = dict(required=False, type='str')
    argspec['secret'] = dict(required=False, type='str', default='notspecified')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_approle_role_secret_create(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_approle_role_secret_create(module):
    params = module.params
    state = params.get('state')
    name = params.get('name')
    mount_point = params.get('mount_point')

    client = hashivault_auth_client(params)
    if state == 'present':
        custom_secret_id = params.get('secret_id')
        cidr_list = params.get('cidr_list')
        metadata = params.get('metadata')
        wrap_ttl = params.get('wrap_ttl')
        if custom_secret_id is not None:
            if module.check_mode:
                try:
                    client.get_role_secret_id(name, custom_secret_id, mount_point=mount_point)
                except Exception:
                    return {'changed': True}
                return {'changed': False}
            result = client.create_role_custom_secret_id(role_name=name,
                                                         mount_point=mount_point,
                                                         secret_id=custom_secret_id,
                                                         meta=metadata)
        else:
            if module.check_mode:
                return {'changed': True}
            result = client.create_role_secret_id(role_name=name,
                                                  mount_point=mount_point,
                                                  meta=metadata,
                                                  cidr_list=cidr_list,
                                                  wrap_ttl=wrap_ttl)

        if wrap_ttl is None:
            response_key = 'data'
        else:
            response_key = 'wrap_info'

        return {'changed': True, response_key: result.get(response_key, {})}
    elif state == 'absent':
        secret = params.get('secret')
        if module.check_mode:
            try:
                client.get_role_secret_id(name, secret, mount_point=mount_point)
            except Exception:
                return {'changed': False}
            return {'changed': True}
        else:
            client.delete_role_secret_id(name, secret, mount_point=mount_point)
        return {'changed': True}
    else:
        return {'failed': True, 'msg': 'Unkown state value: {}'.format(state)}


if __name__ == '__main__':
    main()
