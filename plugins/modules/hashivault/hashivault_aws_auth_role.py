#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

from hvac.exceptions import InvalidPath


ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_aws_auth_role
version_added: "4.4.8"
short_description: Hashicorp Vault aws auth create role module
description:
    - Module to create an aws auth role
options:
    name:
        description:
            - role name.
    auth_type:
        description:
            -  auth type permitted for this role. Valid choices are ec2 and iam
    bound_ami_id:
        description:
            - Defines a constraint on the EC2 instances that can perform the login operation that they should be using\
             the AMI ID specified
    bound_account_id:
        description:
            - Defines a constraint on the EC2 instances that can perform the login operation that they should be using\
             the account ID
    bound_region:
        description:
            - The bound region for the role
    bound_vpc_id:
        description:
            - Defines a constraint on the EC2 instances that can perform the login operation that they be associated\
             with the VPC ID that matches the value
    bound_subnet_id:
        description:
            - Defines a constraint on the EC2 instances that can perform the login operation that they be associated\
             with the subnet ID
    bound_iam_role_arn:
        description:
            - Defines a constraint on the EC2 instances that can perform the login operation that they must match the\
             IAM role ARN
    bound_iam_instance_profile_arn:
        description:
            - Defines a constraint on the EC2 instances that can perform the login operation that they must be\
             associated with an IAM instance profile
    bound_ec2_instance_id:
        description:
            -EC2 instance id
    role_tag:
        description:
            - Role tag
    bound_iam_principal_arn:
        description:
            - IAM principal arn
    inferred_entity_type:
        description:
            - Instructs Vault to turn on inferencing. The only valid value is ec2_instance
    resolve_aws_unique_ids:
        description:
            - If set to true, the bound_iam_principal_arn is resolved to an AWS Unique ID for the bound principal ARN.
    ttl:
        description:
            - The TTL period of tokens issued using this role, provided as a number of seconds.
    max_ttl:
        description:
            - The maximum allowed lifetime of tokens issued using this role, provided as a number of seconds
    period:
        description:
            - The period
    policies:
        description:
            - policies for the role.
    allow_instance_migration:
        description:
            - If set to true, allows migration of the underlying instance where the client resides.
    disallow_reauthentication:
        description:
            - If set to true, only allows a single token to be granted per instance ID.
    mount_point:
        description:
            - location where this auth_method will be mounted. also known as "path"
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_aws_auth_role:
        name: myrole
        auth_type: iam
        inferred_entity_type: ec2_instance
        inferred_aws_region: eu-west-1
        bound_iam_role_arn: arn:aws:iam::12345678:root/ec2-role
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['auth_type'] = dict(required=False, type='str')
    argspec['resolve_aws_unique_ids'] = dict(required=False, type='bool')
    argspec['bound_ami_id'] = dict(required=False, type='str')
    argspec['bound_account_id'] = dict(required=False, type='str')
    argspec['bound_region'] = dict(required=False, type='str')
    argspec['bound_vpc_id'] = dict(required=False, type='str')
    argspec['bound_subnet_id'] = dict(required=False, type='str')
    argspec['bound_iam_role_arn'] = dict(required=False, type='str')
    argspec['bound_iam_instance_profile_arn'] = dict(required=False, type='str')
    argspec['bound_ec2_instance_id'] = dict(required=False, type='str')
    argspec['role_tag'] = dict(required=False, type='str')
    argspec['bound_iam_principal_arn'] = dict(required=False, type='str')
    argspec['inferred_entity_type'] = dict(required=False, type='str')
    argspec['inferred_aws_region'] = dict(required=False, type='str')
    argspec['ttl'] = dict(required=False, type='int')
    argspec['max_ttl'] = dict(required=False, type='int')
    argspec['period'] = dict(required=False, type='int')
    argspec['policies'] = dict(required=False, type='list')
    argspec['allow_instance_migration'] = dict(required=False, type='bool')
    argspec['disallow_reauthentication'] = dict(required=False, type='bool')
    argspec['mount_point'] = dict(required=False, default='aws', type='str')
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    module = hashivault_init(argspec)
    result = hashivault_aws_auth_role(module.params)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_aws_auth_role(params):
    state = params.get('state')
    name = params.get('name').strip('/')
    mount_point = params.get('mount_point').strip('/')
    desired_state = {
        'auth_type': params.get('auth_type'),
        'resolve_aws_unique_ids': params.get('resolve_aws_unique_ids'),
        'bound_ami_id': params.get('bound_ami_id'),
        'bound_account_id': params.get('bound_account_id'),
        'bound_region': params.get('bound_region'),
        'bound_vpc_id': params.get('bound_vpc_id'),
        'bound_subnet_id': params.get('bound_subnet_id'),
        'bound_iam_role_arn': params.get('bound_iam_role_arn'),
        'bound_iam_instance_profile_arn': params.get('bound_iam_instance_profile_arn'),
        'bound_ec2_instance_id': params.get('bound_ec2_instance_id'),
        'role_tag': params.get('role_tag'),
        'bound_iam_principal_arn': params.get('bound_iam_principal_arn'),
        'inferred_entity_type': params.get('inferred_entity_type'),
        'inferred_aws_region': params.get('inferred_aws_region'),
        'ttl': params.get('ttl'),
        'max_ttl': params.get('max_ttl'),
        'period': params.get('period'),
        'policies': params.get('policies'),
        'allow_instance_migration': params.get('allow_instance_migration'),
        'disallow_reauthentication': params.get('disallow_reauthentication'),
    }
    client = hashivault_auth_client(params)
    if not name:
        name = mount_point

    if state == 'present':
        client.auth.aws.create_role(name, mount_point=mount_point, **desired_state)
        return {'changed': True}
    client.auth.aws.delete_role(name, mount_point)
    return {'changed': True}


if __name__ == '__main__':
    main()
