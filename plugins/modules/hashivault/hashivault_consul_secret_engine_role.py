#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_consul_secret_engine_role
version_added: "4.4.7"
short_description: Hashicorp Vault database secret engine role
description:
    - Module to define a database role that vault can generate dynamic credentials for vault
options:
    mount_point:
        description:
            - name of the secret engine mount name.
        default: consul
    name:
        description:
            - Specifies the name of an existing role against which to create this Consul credential
    token_type:
        description:
            - Specifies the type of token to create when using this role. choices: client, management
        default: client
    policy:
        description:
            - Specifies the base64 encoded ACL policy. This is required unless the token_type is management
        default: ""
    policies:
        description:
            - The list of policies to assign to the generated token. This is only available in Consul 1.4 and greater.
        default: []
    local:
        description:
            - Indicates that the token should not be replicated globally and instead be local to the current datacenter.
            - Only available in Consul 1.4 and greater.
        default: false
    ttl:
        description:
            - Specifies the TTL for this role.
            - This is provided as a string duration with a time suffix like "30s" or "1h" or as seconds.
            - If not provided, the default Vault TTL is used.
        default: ""
    max_ttl:
        description:
            - Specifies the max TTL for this role.
            - This is provided as a string duration with a time suffix like "30s" or "1h" or as seconds.
            - If not provided, the default Vault Max TTL is used.
        default: ""
    state:
        description:
            - state of the object. choices: present, absent
        default: present
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
      hashivault_consul_secret_engine_role:
        name: tester
        policy: pocketknife
        state: present
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='consul')
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['token_type'] = dict(required=False, type='str', default='client', choices=['client', 'management'])
    argspec['policy'] = dict(required=False, type='str')
    argspec['policies'] = dict(required=False, type='list')
    argspec['local'] = dict(required=False, type='bool', default=False)
    argspec['ttl'] = dict(required=False, type='int', default=0)
    argspec['max_ttl'] = dict(required=False, type='int', default=0)

    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_consul_secret_engine_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_consul_secret_engine_role(module):
    params = module.params
    client = hashivault_auth_client(params)
    name = params.get('name').strip('/')
    mount_point = params.get('mount_point').strip('/')
    state = params.get('state')

    desired_state = dict()
    desired_state['token_type'] = params.get('token_type')
    desired_state['policy'] = params.get('policy')
    desired_state['policies'] = params.get('policies')
    desired_state['local'] = params.get('local')
    desired_state['ttl'] = params.get('ttl')
    desired_state['max_ttl'] = params.get('max_ttl')

    if state == "present" and desired_state['token_type'] == "client" and \
            (not desired_state['policy'] and not desired_state['policies']):
        return {'failed': True, 'msg': 'provide policy or policies for client token', 'rc': 1}

    if (mount_point + "/") not in client.sys.list_mounted_secrets_engines()['data']:
        return {'failed': True, 'msg': 'secret engine is not enabled', 'rc': 1}

    exists = False
    changed = False
    try:
        current_state = client.secrets.consul.read_role(name, mount_point=mount_point)['data']
        exists = True
        if state == 'absent':
            changed = True
        for key in desired_state.keys():
            if key not in current_state:
                continue
            elif desired_state[key] != current_state[key]:
                changed = True
    except Exception:
        pass

    if not exists and state == 'present':
        changed = True

    if not changed or module.check_mode:
        return {'changed': changed}

    if state == 'present':
        client.secrets.consul.create_or_update_role(name, mount_point=mount_point, **desired_state)
    elif state == 'absent':
        client.secrets.consul.delete_role(name, mount_point=mount_point)

    return {'changed': changed}


if __name__ == '__main__':
    main()
