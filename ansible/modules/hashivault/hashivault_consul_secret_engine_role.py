#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_consul_secret_engine_role
version_added: "4.1.0"
short_description: Hashicorp Vault database secret engine role
description:
    - Module to define a database role that vault can generate dynamic credentials for vault
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
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
      hashivault_consul_secret_engine_role:
        name: tester
        state: present
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='consul')
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['token_type'] = dict(required=False, type='str', default='client', choices=['client', 'management'])
    argspec['policy'] = dict(required=False, type='str', default='')
    argspec['policies'] = dict(required=False, type='list', default=[])
    argspec['local'] = dict(required=False, type='bool', default=False)
    argspec['ttl'] = dict(required=False, type='str', default='')
    argspec['max_ttl'] = dict(required=False, type='str', default='')

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_consul_secret_engine_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_consul_secret_engine_role(module):
    params = module.params
    client = hashivault_auth_client(params)
    name = params.get('name')
    mount_point = params.get('mount_point')
    state = params.get('state')
    desired_state = dict()
    exists = False
    changed = False

    desired_state['token_type'] = params.get('token_type')
    desired_state['policy'] = params.get('policy')
    desired_state['policies'] = params.get('policies')
    desired_state['local'] = params.get('local')
    desired_state['ttl'] = params.get('ttl')
    desired_state['max_ttl'] = params.get('max_ttl')

    if mount_point[-1]:
        mount_point = mount_point.strip('/')

    if name[-1] == '/':
        name = name.strip('/')

    if state == "present" and \
            desired_state['token_type'] == "client" and \
            (desired_state['policy'] == "" and len(desired_state['policies']) == 0):
        return {'failed': True, 'msg': 'provide policy or policies for client token', 'rc': 1}

    if (mount_point + "/") not in client.sys.list_mounted_secrets_engines()['data'].keys():
        return {'failed': True, 'msg': 'secret engine is not enabled', 'rc': 1}

    # check if role exists
    try:
        client.secrets.consul.read_role(name, mount_point=mount_point)
        exists = True
    except Exception:
        pass

    if (exists and state == 'absent') or (not exists and state == 'present'):
        changed = True

    # compare current_state to desired_state
    if exists and state == 'present' and not changed:
        current_state = client.secrets.consul.read_role(name, mount_point=mount_point)['data']
        for k, v in desired_state.items():
            if k in current_state and v != current_state[k]:
                changed = True
    elif exists and state == 'absent':
        changed = True

    if changed and state == 'present' and not module.check_mode:
        client.secrets.consul.create_or_update_role(name, mount_point=mount_point, **desired_state)

    elif changed and state == 'absent' and not module.check_mode:
        client.secrets.consul.delete_role(name, mount_point=mount_point)

    return {'changed': changed}


if __name__ == '__main__':
    main()
