#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json

DOCUMENTATION = '''
module: hashivault_googlecloud_configure
version_added: "1.0.0"
short_description: Hashicorp Vault googlecloud management role module
description:
    - Module to manage an googlecloud configuration from Hashicorp Vault.
options:
    credentials:
        description:
            - A JSON string containing the contents of a GCP credentials file.
    credentials_file:
        description:
            - A JSON string containing the contents of a GCP credentials file.
    iam_alias:
        description:
            - role_id or unique_id
    iam_metadata:
        description:
            - The metadata to include on the token returned by the login endpoint
        default: default
    gce_alias:
        description:
            -   instance_id or role_id
    gce_metadata:
        description:
            -  The metadata to include on the token returned by the login endpoint
        default: default
    mount_point:
        description:
            - mount point for Google Cloud Configuration
        default: gcp
    state:
        description:
            - present or absent
        default: present
'''


def main():
    argspec = hashivault_argspec()
    argspec['credentials'] = dict(required=False, type='str')
    argspec['credentials_file'] = dict(required=False, type='str')
    argspec['iam_alias'] = dict(required=False, type='str', choices=['unique_id', 'role_id'], default='role_id')
    argspec['iam_metadata'] = dict(required=False, type='str', default='default')
    argspec['gce_alias'] = dict(required=False, type='str', choices=['instance_id', 'role_id'], default='role_id')
    argspec['gce_metadata'] = dict(required=False, type='str', default='default')
    argspec['mount_point'] = dict(required=False, type='str', default='gcp')
    argspec['state'] = dict(required=False, type='str', choices=['present', 'absent'], default='present')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_googlecloud_configure(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_googlecloud_configure(module):
    params = module.params
    state = params.get('state')
    credentials = params.get('credentials')
    credentials_file = params.get('credentials_file')
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point').strip('/')
    desired_state = dict()
    current_state = dict()
    changed = False

    if credentials_file:
        desired_state['credentials'] = json.dumps(json.load(open(params.get('credentials_file'), 'r')))
    elif credentials:
        desired_state['credentials'] = params.get('credentials')

    try:
        current_state = client.auth.gcp.read_config()
    except Exception:
        changed = True

    if changed and not module.check_mode and state == 'present':
        client.auth.gcp.configure(mount_point=mount_point, **desired_state)
        return {'changed': True}
    else:
        client.auth.gcp.delete_config(mount_point=mount_point)
        return {'changed': True}


if __name__ == '__main__':
    main()

