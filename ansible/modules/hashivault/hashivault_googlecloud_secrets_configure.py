#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json


def main():
    argspec = hashivault_argspec()
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['ttl'] = dict(required=False, type='int', default='3600')
    argspec['max_ttl'] = dict(required=False, type='int')
    argspec['mount_point'] = dict(required=False, type='str', default='gcp')
    argspec['credentials'] = dict(required=False, type='str')
    argspec['credentials_file'] = dict(required=False, type='str')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_googlecloud_secrets_configure(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_googlecloud_secrets_configure(module):
    params = module.params
    client = hashivault_auth_client(params)
    state = params.get('state')
    mount_point = params.get('mount_point').strip('/')
    credentials = params.get('credentials')
    credentials_file = params.get('credentials_file')
    ttl = params.get('ttl')
    max_ttl = params.get('max_ttl')
    desired_state = dict()
    current_state = dict()
    changed = False

    if credentials_file:
        with open(credentials_file) as creds:
            data = json.load(creds)
            credential = json.dumps(data)
        desired_state['credentials'] = credential
        desired_state['ttl'] = ttl
        desired_state['max_ttl'] = max_ttl
    elif credentials:
        desired_state['credentials'] = credentials
        desired_state['ttl'] = ttl
        desired_state['max_ttl'] = max_ttl

    try:
        current_state = client.secrets.gcp.read_config()
    except Exception:
        changed = True

    if changed and not module.check_mode and state == 'present':
        client.secrets.gcp.configure(mount_point=mount_point, **desired_state)

    return {'changed': True}


if __name__ == '__main__':
    main()
