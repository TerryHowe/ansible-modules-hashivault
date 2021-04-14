#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json


def main():
    argspec = hashivault_argspec()
    argspec['credentials_file'] = dict(required=False, type='str')
    argspec['ttl'] = dict(required=False, type='int', default=0)
    argspec['max_ttl'] = dict(required=False, type='int', default=0)
    argspec['mount_point'] = dict(required=False, type='str', default='gcp')
    argspec['state'] = dict(required=False, type='str', choices=['present', 'absent'], default='present')
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
    credentials_file = params.get('credentials_file')
    state = params.get('state')
    desired_state = dict()

    desired_state['credentials'] = json.dumps(json.load(open(params.get(credentials_file))))
    desired_state['ttl'] = params.get('ttl')
    desired_state['max_ttl'] = params.get('max_ttl')

    exists = False
    current_state = {}

    try:
        current_state = client.secrets.gcp.read_config(mount_point=params.get('mount_point'))
    except Exception:
        pass

    if state == 'present' and not module.check_mode:
        client.secrets.gcp.configure(mount_point=params.get('mount_point'), **desired_state)
    else:
        client.secrets.gcp.read_config(mount_point=params.get('mount_point'))


if __name__ == '__main__':
    main()
