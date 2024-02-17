#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper


def main():
    argspec = hashivault_argspec()
    argspec['role_name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='gcp')
    argspec['add'] = dict(required=False, type='list', default=[])
    argspec['remove'] = dict(required=False, type='list', default=[])
    module = hashivault_init(argspec)
    result = hashivault_googlecloud_auth_edit_service_account(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_googlecloud_auth_edit_service_account(module):
    params = module.params
    client = hashivault_auth_client(params)
    role_name = params.get('role_name').strip('/')
    mount_point = params.get('mount_point').strip('/')
    add = params.get('add')
    remove = params.get('remove')
    changed = False
    desired_state = dict()

    if add:
        desired_state['add'] = params.get('add')
    if remove:
        desired_state['remove'] = params.get('remove')

    client.auth.gcp.edit_service_accounts_on_iam_role(mount_point=mount_point, name=role_name, **desired_state)

    return {'changed': changed}


if __name__ == '__main__':
    main()
