#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

DEFAULT_TTL = 2764800
ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_namespace
version_added: "4.0.1"
short_description: Hashicorp Vault create / delete namespaces
description:
    - Module to create or delete Hashicorp Vault namespaces (enterprise only)
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
            - name of the namespace
    state:
        description:
            - state of secret backend. choices: present, disabled
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_namespace:
        name: teama

    - name: "create a child namespace 'team1' in 'teama' ns: teama/team1"
      hashivault_namespace:
        name: team1
        namespace: teama
'''

def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['state'] = dict(required=False, type='str', choices=['present', 'absent'], default='present')
    module = hashivault_init(argspec)
    result = hashivault_secret_engine(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_secret_engine(module):
    params = module.params
    client = hashivault_auth_client(params)
    name = params.get('name')
    state = params.get('state')
    current_state = dict()
    exists = False
    changed = False

    try:
        # does the ns exist already?
        current_state = client.sys.list_namespaces()['data']['keys']
        if (name + '/') in current_state:
            exists = True
    except Exception:
        # doesnt exist
        pass
    
    # doesnt exist and should or does exist and shouldnt
    if (exists and state == 'absent') or (not exists and state == 'present'):
        changed = True

    # make changes!
    
    # doesnt exist and should
    if changed and not exists and state == 'present' and not module.check_mode:
        client.sys.create_namespace(path=name)
    
    # exists and shouldnt    
    elif changed and (state == 'absent' or state == 'disabled') and not module.check_mode:
        client.sys.delete_namespace(path=name)

    return {'changed': changed}


if __name__ == '__main__':
    main()
