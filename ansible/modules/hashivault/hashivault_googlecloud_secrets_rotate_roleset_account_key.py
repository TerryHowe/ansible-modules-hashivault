#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='gcp')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_googlecloud_secrets_rotate_roleset_account_key(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_googlecloud_secrets_rotate_roleset_account_key(module):
    params = module.params
    client = hashivault_auth_client(params)
    name = params.get('name')
    mount_point = params.get('mount_point')
    changed = False

    client.secrets.gcp.rotate_roleset_account_key(name=name, mount_point=mount_point)
    return {'changed': True}


if __name__ == '__main__':
    main()
