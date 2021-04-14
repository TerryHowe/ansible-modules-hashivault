#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['secret_type'] = dict(required=False, type='str', choices=['access_token', 'service_account'],
                                  default='access_token')
    argspec['project'] = dict(required=True, type='str')
    argspec['bindings'] = dict(required=True, type='str')
    argspec['token_scopes'] = dict(required=False, type='list', default=[])
    argspec['state'] = dict(required=False, type='str', choices=['present', 'update', 'absent'], default='present')
    argspec['mount_point'] = dict(required=True, type='str')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_googlecloud_secrets_roleset(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_googlecloud_secrets_roleset(module):
    params = module.params
    mount_point = params.get('mount_point')
    desired_state = dict()
    current_state = dict()
    changed = False
    client = hashivault_auth_client(params)
    state = params.get('state')
    name = params.get('name')
    secret_type = params.get('secret_type')
    project = params.get('project')

    desired_state['name'] = name
    desired_state['secret_type'] = secret_type
    desired_state['project'] = project
    desired_state['bindings'] = params.get('bindings')

    if secret_type == 'access_token':
        desired_state['token_scopes'] = params.get('token_scopes')

    try:
        current_state = client.secrets.read_roleset()
    except Exception:
        changed = True

    if state == 'present' or state == 'update':
        client.secrets.create_or_update_roleset(mount_point=mount_point, **desired_state)
    else:
        client.secrets.delete_roleset(mount_point=mount_point, name=name)


if __name__ == '__main__':
    main()
