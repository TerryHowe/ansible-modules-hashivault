#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

DEFAULT_TTL = 2764800
ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_secret_engine
version_added: "3.17.8"
short_description: Hashicorp Vault secret enable/disable module
description:
    - Module to enable secret backends in Hashicorp Vault.
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
            - name of secret backend
    backend:
        description:
            - type of secret backend
    description:
        description:
            - description of secret backend
    config:
        description:
            - config of secret backend
        default: {'default_lease_ttl': 2764800, 'max_lease_ttl': 2764800, 'force_no_cache': False}
    state:
        description:
            - state of secret backend. choices: enabled, present, disabled, absent
    options:
        description:
            - Specifies mount type specific options that are passed to the backend. NOT included unless backend == kv
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_secret_engine:
        name: ephemeral
        backend: generic
'''

def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['backend'] = dict(required=False, type='str', default='')
    argspec['description'] = dict(required=False, type='str')
    argspec['config'] = dict(required=False, type='dict', default={'default_lease_ttl': DEFAULT_TTL, 'max_lease_ttl': DEFAULT_TTL, 'force_no_cache': False})
    argspec['state'] = dict(required=False, type='str', choices=['present', 'enabled', 'absent', 'disabled'], default='present')
    argspec['options'] = dict(required=False, type='dict', default={'version': '1'})
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
    backend = params.get('backend')
    description = params.get('description')
    config = params.get('config')
    state = params.get('state')
    options = params.get('options')
    current_state = dict()
    exists = False
    created = False
    changed = False

    if not backend:
        backend = name
    try:
        # does the mount exist already?
        current_state = client.sys.read_mount_configuration(path=name)['data']
        exists = True
    except Exception:
        # doesnt exist
        pass
    
    # doesnt exist and should or does exist and shouldnt
    if (exists and state == 'absent') or (exists and state == 'disabled') or (not exists and state == 'present') or (not exists and state == 'enabled'):
        changed = True

    # want to exist so we'll check current state against desired state
    if not changed and (state == 'present' or state == 'enabled'):
        # verify config has ['default_lease_ttl: DEFAULT_TTL', 'max_lease_ttl: DEFAULT_TTL, 'force_no_cache': False']
        if 'default_lease_ttl' not in config:
            config['default_lease_ttl'] = DEFAULT_TTL
        if 'max_lease_ttl' not in config:
            config['max_lease_ttl'] = DEFAULT_TTL
        if 'force_no_cache' not in config:
            config['force_no_cache'] = False
        options['version'] = str(options['version'])

        for k, v in current_state.items(): #while not changed?
            # options is passed in ['data'] but set outside 'config':{}, manually check
            if k == 'options':
                if v != options:
                    changed = True
            elif v != config[k]:
                changed = True
        
    # make changes!
    # only pass 'options' when working on a kv backend
    
    # doesnt exist and should
    if changed and not exists and (state == 'present' or state == 'enabled') and not module.check_mode:
        if backend == 'kv':
            client.sys.enable_secrets_engine(backend, description=description, path=name, config=config, options=options)
        else:
            client.sys.enable_secrets_engine(backend, description=description, path=name, config=config)
        created = True
        
    # needs to be updated
    elif changed and exists and (state == 'present' or state == 'enabled') and not module.check_mode:
        if backend == 'kv':
            client.sys.tune_mount_configuration(description=description, path=name, options=options, **config)
        else:
            client.sys.tune_mount_configuration(description=description, path=name, **config)
    
    # exists and shouldnt    
    elif changed and (state == 'absent' or state == 'disabled') and not module.check_mode:
        client.sys.disable_secrets_engine(path=name)

    return {'changed': changed, 'created': created}


if __name__ == '__main__':
    main()
