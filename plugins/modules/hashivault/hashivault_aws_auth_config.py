#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

from hvac.exceptions import InvalidPath


ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_aws_auth_config
version_added: "4.4.8"
short_description: Hashicorp Vault aws auth configure module
description:
    - Module to configure an aws auth backend
options:
    max_retries:
        description:
            - Number of max retries the client should use for recoverable errors.
    access_key:
        description:
            - AWS Access key with permissions to query AWS APIs.
    secret_key:
        description:
            - AWS Secret key with permissions to query AWS APIs
    endpoint:
        description:
            - URL to override the default generated endpoint for making AWS EC2 API calls
    iam_endpoint:
        description:
            - URL to override the default generated endpoint for making AWS IAM API calls
    sts_endpoint:
        description:
            - URL to override the default generated endpoint for making AWS STS API calls
    iam_server_id_header_value:
        description:
            - The value to require in the X-Vault-AWS-IAM-Server-ID header
    mount_point:
        description:
            - location or "path" where this auth method is mounted
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_aws_auth_config:
        mount_point: myaws
        access_key: AwesomeAccessK3y
        secret_key: N0b0dyKnows
'''


def main():
    argspec = hashivault_argspec()
    argspec['max_retries'] = dict(required=False, type='int')
    argspec['access_key'] = dict(required=False, type='str')
    argspec['secret_key'] = dict(required=False, type='str')
    argspec['endpoint'] = dict(required=False, type='str')
    argspec['iam_endpoint'] = dict(required=False, type='str')
    argspec['sts_endpoint'] = dict(required=False, type='str')
    argspec['iam_server_id_header_value'] = dict(required=False, type='str')
    argspec['mount_point'] = dict(required=False, default='aws', type='str')
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    module = hashivault_init(argspec)
    result = hashivault_aws_auth_config(module.params)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_aws_auth_config(params):
    state = params.get('state')
    mount_point = params.get('mount_point').strip('/')
    desired_state = {
        'max_retries': params.get('max_retries'),
        'access_key': params.get('access_key'),
        'secret_key': params.get('secret_key'),
        'endpoint': params.get('endpoint'),
        'iam_endpoint': params.get('iam_endpoint'),
        'sts_endpoint': params.get('sts_endpoint'),
        'iam_server_id_header_value': params.get('iam_server_id_header_value'),
    }
    client = hashivault_auth_client(params)

    if state == 'present':
        client.auth.aws.configure(mount_point=mount_point, **desired_state)
        return {'changed': True}
    client.auth.aws.delete_config(mount_point)
    return {'changed': True}


if __name__ == '__main__':
    main()
