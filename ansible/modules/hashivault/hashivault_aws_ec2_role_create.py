#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

from hvac.exceptions import InvalidPath


ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_aws_ec2_role_create
version_added: "3.9.8"
short_description: Hashicorp Vault aws ec2 create role module
description:
    - Module to create a aws ec2 backed vault role
options:
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    ca_cert:
        description:
            - "path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate"
        default: to environment variable VAULT_CACERT
    ca_path:
        description:
            - "path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate : if ca_cert
             is specified, its value will take precedence"
        default: to environment variable VAULT_CAPATH
    client_cert:
        description:
            - "path to a PEM-encoded client certificate for TLS authentication to the Vault server"
        default: to environment variable VAULT_CLIENT_CERT
    client_key:
        description:
            - "path to an unencrypted PEM-encoded private key matching the client certificate"
        default: to environment variable VAULT_CLIENT_KEY
    verify:
        description:
            - "if set, do not verify presented TLS certificate before communicating with Vault server : setting this
             variable is not recommended except during testing"
        default: to environment variable VAULT_SKIP_VERIFY
    authtype:
        description:
            - "authentication type to use: token, userpass, github, ldap, approle"
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
        default: to environment variable VAULT_USER
    password:
        description:
            - password to login to vault.
        default: to environment variable VAULT_PASSWORD
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
    client = hashivault_auth_client(params)
    kwargs = {
        'policies': policies,
    }
    for arg in args:
        value = params.get(arg)
        if value is not None:
            kwargs[arg] = value

    if 'aws/' not in client.sys.list_auth_methods().keys():
        return {'failed': True, 'msg': 'aws auth backend is not enabled', 'rc': 1}

    try:
        if client.get_role(name, 'aws'):
            return {'changed': False}
    except InvalidPath:
        client.create_role(name, mount_point='aws', **kwargs)
        return {'changed': True}


if __name__ == '__main__':
    main()
