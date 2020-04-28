#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_consul_secret_engine_config
version_added: "4.4.7"
short_description: Hashicorp Vault consul secrets engine config
description:
    - Module to configure the consul secrets engine
options:
    mount_point:
        description:
            - name of the secret engine mount name.
        default: consul
    consul_address:
        description:
            - Specifies the address of the Consul instance, provided as "host:port" like "127.0.0.1:8500"
    scheme:
        description:
            -  Specifies the URL scheme to use
    consul_token:
        description:
            - Specifies the Consul ACL token to use. This must be a management type token.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_consul_secret_engine_config:
        consul_address: consul.local:8500
        scheme: https
        consul_token: myAwesomeConsulManagementToken
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='consul')
    argspec['consul_address'] = dict(required=True, type='str')
    argspec['scheme'] = dict(required=True, type='str')
    argspec['consul_token'] = dict(required=True, type='str')

    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_consul_secret_engine_config(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_consul_secret_engine_config(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point').strip('/')
    consul_address = params.get('consul_address')
    scheme = params.get('scheme')
    token = params.get('consul_token')

    if (mount_point + "/") not in client.sys.list_mounted_secrets_engines()['data']:
        return {'failed': True, 'msg': 'Consul secret engine is not enabled', 'rc': 1}

    if module.check_mode:
        return {'changed': True}

    response = client.secrets.consul.configure_access(consul_address, token, scheme=scheme, mount_point=mount_point)
    if response.ok:
        return {'changed': True}
    return {'failed': True, 'msg': response.text}


if __name__ == '__main__':
    main()
