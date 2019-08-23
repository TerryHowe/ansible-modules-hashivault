#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_consul_secret_engine_config
version_added: "4.1.0"
short_description: Hashicorp Vault consul secrets engine config
description:
    - Module to configure the consul secrets engine 
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
    address:
        description:
            - Specifies the address of the Consul instance, provided as "host:port" like "127.0.0.1:8500"
    scheme:
        description:
            -  Specifies the URL scheme to use
    consul_token:
        description:
            - Specifies the Consul ACL token to use. This must be a management type token.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_consul_secret_engine_config:
        address: consul.local:8500
        scheme: https
        token: myAwesomeConsulManagementToken
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='consul')
    argspec['address'] = dict(required=True, type='str')
    argspec['scheme'] = dict(required=True, type='str')
    argspec['consul_token'] = dict(required=True, type='str')

    supports_check_mode=True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_consul_secret_engine_config(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_consul_secret_engine_config(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point')
    address = params.get('address')
    scheme = params.get('scheme')
    token = params.get('consul_token')

    if mount_point[-1]:
        mount_point = mount_point.strip('/')

    if (mount_point + "/") not in client.sys.list_mounted_secrets_engines()['data'].keys():
        return {'failed': True, 'msg': 'secret engine is not enabled', 'rc': 1}

    if not module.check_mode:
        response = client.secrets.consul.configure_access(address, token, scheme=scheme, mount_point=mount_point)

        return {'changed': True} if response.ok else {'failed': True, 'msg': response.text}

    return {'changed': True}


if __name__ == '__main__':
    main()
