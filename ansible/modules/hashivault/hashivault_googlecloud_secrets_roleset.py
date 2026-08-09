#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['project'] = dict(required=True, type='str')
    argspec['secret_type'] = dict(required=True, type='str', default=None,
                                  choices=['access_token', 'service_account_key'])
    argspec['bindings'] = dict(required=True, type='str')
    argspec['token_scopes'] = dict(required=False, type='list', default=[])
    argspec['mount_point'] = dict(required=False, type='str', default='gcp')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_googlecloud_secrets_roleset(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_googlecloud_secrets_roleset(module):
    params = module.params
    client = hashivault_auth_client(params)
    state = params.get('state')
    mount_point = params.get('mount_point').strip('/')
    project = params.get('project')
    bindings = params.get('bindings')
    secret_type = params.get('secret_type')
    name = params.get('name')
    token_scopes = params.get('token_scopes')
    desired_state = dict()
    current_state = dict()
    changed = False

    if secret_type == 'access_token':
        desired_state['token_scopes'] = token_scopes
    elif secret_type == 'service_account_key':
        desired_state['bindings'] = bindings
    elif secret_type is None:
        desired_state['bindings'] = bindings
        desired_state['token_scopes'] = token_scopes

    try:
        current_state = client.secrets.gcp.read_roleset(name=name)
    except Exception:
        changed = True

    if changed and not module.check_mode and state == 'present':
        client.secrets.gcp.create_or_update_roleset(mount_point=mount_point, name=name, project=project
                                                    , **desired_state)

    return {'changed': True}


if __name__ == '__main__':
    main()
