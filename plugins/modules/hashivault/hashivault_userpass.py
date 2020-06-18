#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_userpass
version_added: "3.12.0"
short_description: Hashicorp Vault userpass user management module
description:
    - Module to manage userpass users in Hashicorp Vault.
options:
    name:
        description:
            - user name to create.
    pass:
        description:
            - user to create password.
    pass_update:
        description:
            - whether to update the password if user exists
        default: False
    policies:
        description:
            - user policies.
        default: default
    token_bound_cidrs:
        description:
            - List of CIDR blocks; if set, specifies blocks of IP addresses which can authenticate successfully, and
              ties the resulting token to these blocks as well.
    state:
        description:
            - whether create/update or delete the user
    mount_point:
        description:
            - default The "path" (app-id) the auth backend is mounted on.
        default: userpass
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_userpass_create:
      name: 'bob'
      pass: 'S3cre7s'
      policies: 'bob'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['pass'] = dict(required=False, type='str', default=None, no_log=True)
    argspec['pass_update'] = dict(required=False, type='bool', default=False)
    argspec['policies'] = dict(required=False, type='list', default=[])
    argspec['token_bound_cidrs'] = dict(required=False, type='list', default=[])
    argspec['state'] = dict(required=False, choices=['present', 'absent'], default='present')
    argspec['mount_point'] = dict(required=False, type='str', default='userpass')
    module = hashivault_init(argspec)
    result = hashivault_userpass(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def hashivault_userpass_update(client, user_details, user_name, user_pass, user_pass_update, user_policies,
                               mount_point, token_bound_cidrs):
    policies_changed = False
    token_bound_cidrs_changed = False
    password_change_allowed = user_pass_update and user_pass

    if set(user_details['data'].get('policies', [])) != set(user_policies):
        policies_changed = True

    if set(user_details['data']['token_bound_cidrs']) != set(token_bound_cidrs):
        token_bound_cidrs_changed = True

    attribute_changed = policies_changed or token_bound_cidrs_changed

    if password_change_allowed and not attribute_changed:
        client.update_userpass_password(user_name, user_pass, mount_point=mount_point)
        return {'changed': True}

    if password_change_allowed and attribute_changed:
        client.create_userpass(user_name, user_pass, user_policies, mount_point=mount_point,
                               token_bound_cidrs=token_bound_cidrs)
        return {'changed': True}

    if not password_change_allowed and attribute_changed:
        if token_bound_cidrs_changed:
            err_msg = u"token_bound_cidrs can only be changed if user_pass is specified and user_pass_update is True"
            return {
                'rc': 1,
                'failed': True,
                'msg': err_msg
            }

        if policies_changed:
            client.update_userpass_policies(user_name, user_policies, mount_point=mount_point)
            return {'changed': True}

    return {'changed': False}


@hashiwrapper
def hashivault_userpass(params):
    client = hashivault_auth_client(params)
    state = params.get('state')
    name = params.get('name')
    password = params.get('pass')
    password_update = params.get('pass_update')
    policies = params.get('policies')
    token_bound_cidrs = params.get('token_bound_cidrs')
    mount_point = params.get('mount_point')
    if state == 'present':
        try:
            user_details = client.read_userpass(name, mount_point=mount_point)
        except Exception:
            if password is not None:
                client.create_userpass(name, password, policies, token_bound_cidrs=token_bound_cidrs,
                                       mount_point=mount_point)
                return {'changed': True}
            else:
                return {'failed': True, 'msg': 'pass must be provided for new users'}
        else:
            return hashivault_userpass_update(client, user_details, user_name=name, user_pass=password,
                                              user_pass_update=password_update, user_policies=policies,
                                              mount_point=mount_point, token_bound_cidrs=token_bound_cidrs)
    elif state == 'absent':
        try:
            client.read_userpass(name, mount_point=mount_point)
        except Exception:
            return {'changed': False}
        else:
            client.delete_userpass(name, mount_point=mount_point)
            return {'changed': True}
    else:
        return {'failed': True, 'msg': 'Unkown state type'}


if __name__ == '__main__':
    main()
