#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

from hvac.exceptions import InvalidPath


ANSIBLE_METADATA = {'status': ['deprecated'], 'alternative': 'Use M(hashivault_aws_auth_role) instead.',
                    'why': 'This module does not fit the standard pattern',
                    'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_aws_ec2_role_create
version_added: "3.9.8"
short_description: Hashicorp Vault aws ec2 create role module
description:
    - Module to create a aws ec2 backed vault role Use hashivault_aws_auth_role instead.
options:
    name:
        description:
            - role name.
    bound_ami_id:
        description:
            - "defines a constraint on the EC2 instances that can perform the login operation that they should be using\
             the AMI ID specified"
    bound_vpc_id:
        description:
            - "defines a constraint on the EC2 instances that can perform the login operation that they be associated\
             with the VPC ID that matches the value"
    policies:
        description:
            - policies for the role.
    inferred_entity_type:
        description:
            - Instructs Vault to turn on inferencing. The only valid value is ec2_instance
    auth_type:
        description:
            -  auth type permitted for this role. Valid choices are ec2 and iam
    bound_account_id:
        description:
            - "defines a constraint on the EC2 instances that can perform the login operation that they should be using\
             the account ID"
    bound_iam_instance_profile_arn:
        description:
            - "defines a constraint on the EC2 instances that can perform the login operation that they must be\
             associated with an IAM instance profile"
    bound_iam_role_arn:
        description:
            - "defines a constraint on the EC2 instances that can perform the login operation that they must match the\
             IAM role ARN"
    bound_subnet_id:
        description:
            - "defines a constraint on the EC2 instances that can perform the login operation that they be associated\
             with the subnet ID"
    allow_instance_migration:
        description:
            - if set to true, allows migration of the underlying instance where the client resides.
    disallow_reauthentication:
        description:
            - If set to true, only allows a single token to be granted per instance ID.
    resolve_aws_unique_ids:
        description:
            - If set to true, the bound_iam_principal_arn is resolved to an AWS Unique ID for the bound principal ARN.
    token_max_ttl:
        description:
            - The maximum allowed lifetime of tokens issued using this role, provided as a number of seconds
    token_ttl:
        description:
            - The TTL period of tokens issued using this role, provided as a number of seconds
    mount_point:
        description:
            - location where this auth_method will be mounted. also known as "path"
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_aws_ec2_role_create:
        name: myrole
        auth_type: iam
        inferred_entity_type: ec2_instance
        inferred_aws_region: eu-west-1
        bound_iam_role_arn: arn:aws:iam::12345678:root/ec2-role
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['bound_ami_id'] = dict(required=False, type='str')
    argspec['bound_vpc_id'] = dict(required=False, type='str')
    argspec['inferred_entity_type'] = dict(required=True, type='str')
    argspec['inferred_aws_region'] = dict(required=False, type='str')
    argspec['auth_type'] = dict(required=True, type='str')
    argspec['bound_account_id'] = dict(required=False, type='str')
    argspec['bound_iam_role_arn'] = dict(required=False, type='str')
    argspec['bound_iam_instance_profile_arn'] = dict(required=False, type='str')
    argspec['bound_ec2_instance_id'] = dict(required=False, type='str')
    argspec['bound_subnet_id'] = dict(required=False, type='str')
    argspec['allow_instance_migration'] = dict(required=False, type='bool')
    argspec['disallow_reauthentication'] = dict(required=False, type='bool')
    argspec['resolve_aws_unique_ids'] = dict(required=False, type='bool')
    argspec['token_max_ttl'] = dict(required=False, type='int')
    argspec['token_ttl'] = dict(required=False, type='int')
    argspec['mount_point'] = dict(required=False, default='aws', type='str')
    module = hashivault_init(argspec)
    result = hashivault_aws_ec2_role_create(module.params)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_aws_ec2_role_create(params):
    args = [
        'bound_ami_id',
        'bound_vpc_id',
        'inferred_entity_type',
        'inferred_aws_region',
        'bound_account_id',
        'bound_iam_role_arn',
        'bound_iam_instance_profile_arn',
        'auth_type'
        'bound_ec2_instance_id',
        'allow_instance_migration',
        'disallow_reauthentication',
        'token_ttl',
        'token_max_ttl',
    ]
    name = params.get('name')
    policies = params.get('policies')
    mount_point = params.get('mount_point').strip('/')
    client = hashivault_auth_client(params)
    kwargs = {
        'policies': policies,
    }
    for arg in args:
        value = params.get(arg)
        if value is not None:
            kwargs[arg] = value

    result = client.sys.list_auth_methods()
    backends = result.get('data', result)
    if (mount_point + "/") not in backends:
        return {'failed': True, 'msg': 'aws auth backend is not enabled', 'rc': 1}

    try:
        if client.get_role(name, mount_point):
            return {'changed': False}
    except InvalidPath:
        client.create_role(name, mount_point=mount_point, **kwargs)
        return {'changed': True}


if __name__ == '__main__':
    main()
