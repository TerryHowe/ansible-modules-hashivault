#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['project_id'] = dict(required=True, type='str')
    argspec['role_type'] = dict(required=True, type='str', choices=['gce', 'iam'])
    argspec['mount_point'] = dict(required=False, type='str', default='gcp')
    argspec['bound_service_accounts'] = dict(required=False, type='list', default=[])
    argspec['bound_projects'] = dict(required=False, type='list', default=[])
    argspec['add_group_aliases'] = dict(required=False, type='bool')
    argspec['token_ttl'] = dict(required=False, type='str')
    argspec['token_max_ttl'] = dict(required=False, type='str')
    argspec['token_policies'] = dict(required=False, type='list', default=[])
    argspec['token_bound_cidrs'] = dict(required=False, type='list', default=[])
    argspec['token_explicit_max_ttl'] = dict(required=False, type='str')
    argspec['token_no_default_policy'] = dict(required=False, type='bool', default='false')
    argspec['token_num_uses'] = dict(required=False, type='str')
    argspec['token_period'] = dict(required=False, type='str')
    argspec['token_type'] = dict(required=False, type='str', choices=['service', 'batch', 'default'], default='default')
    argspec['max_jwt_exp'] = dict(required=False, type='str', default='15m')
    argspec['allow_gce_inference'] = dict(required=False, type='bool', default=True)
    argspec['bound_zones'] = dict(required=False, type='list', default=[])
    argspec['bound_regions'] = dict(required=False, type='list', default=[])
    argspec['bound_instance_groups'] = dict(required=False, type='list', default=[])
    argspec['bound_labels'] = dict(required=False, type='list', default=[])
    argspec['state'] = dict(required=False, type='str', default='present')
    module = hashivault_init(argspec)
    result = hashivault_googlecloud_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_googlecloud_role(module):
    params = module.params
    client = hashivault_auth_client(params)
    state = params.get('state')
    name = params.get('name').strip('/')
    mount_point = params.get('mount_point').strip('/')
    project_id = params.get('project_id')
    role_type = params.get('role_type')
    changed = False
    exists = False
    desired_state = dict()

    if role_type == 'iam' and state == 'present':
        args = [
            'project_id',
            'bound_projects',
            'add_group_aliases',
            'token_ttl',
            'token_max_ttl',
            'token_policies',
            'token_bound_cidrs',
            'token_explicit_max_ttl',
            'token_no_default_policy',
            'token_num_uses',
            'token_period',
            'token_type',
            'bound_zones',
            'bound_regions',
            'bound_instance_groups',
            'bound_labels'
        ]
        desired_state = {}
    elif role_type == 'gce' and state == 'present':
        args = [
            'project_id',
            'bound_projects',
            'add_group_aliases',
            'token_ttl',
            'token_max_ttl',
            'token_policies',
            'token_bound_cidrs',
            'token_explicit_max_ttl',
            'token_no_default_policy',
            'token_num_uses',
            'token_period',
            'token_type',
            'max_jwt_exp',
            'allow_gce_inference',
            'bound_service_accounts'
        ]
        desired_state = {}

    try:
        current_state = client.auth.gcp.read_role()
    except Exception:
        changed = True

    if changed and state == 'present' and not module.check_mode:
        client.auth.gcp.create_role(name=name, project_id=project_id, role_type=role_type, mount_point=mount_point, **desired_state)

    elif changed and state == 'absent' and not module.check_mode:
        client.auth.gcp.delete_role(name=name, project_id=project_id, role_type=role_type, mount_point=mount_point)

    return {'changed': changed}


if __name__ == '__main__':
    main()
