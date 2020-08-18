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
    cas_required:
        description:
            - Check and set required for secret engine for kv version 2 only
    max_versions:
        description:
            - Max versions for secret engine for kv version 2 only
extends_documentation_fragment: hashivault
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
    argspec['description'] = dict(required=False, type='str', default='')
    argspec['config'] = dict(required=False, type='dict', default={'default_lease_ttl': DEFAULT_TTL,
                                                                   'max_lease_ttl': DEFAULT_TTL,
                                                                   'force_no_cache': False})
    argspec['state'] = dict(required=False, type='str', choices=['present', 'enabled', 'absent', 'disabled'],
                            default='present')
    argspec['options'] = dict(required=False, type='dict', default={})
    argspec['cas_required'] = dict(required=False, type='bool')
    argspec['max_versions'] = dict(required=False, type='int')
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
    if params.get('state') in ['present', 'enabled']:
        state = 'enabled'
    else:
        state = 'disabled'
    options = params.get('options')
    cas_required = params.get('cas_required')
    max_versions = params.get('max_versions')
    new_engine_configuration = {}
    if str(options.get('version', '1')) == '2':
        if cas_required:
            new_engine_configuration['cas_required'] = cas_required
        if max_versions:
            new_engine_configuration['max_versions'] = max_versions
    current_state = dict()
    exists = False
    created = False
    changed = False

    if not backend:
        backend = name
    try:
        # does the mount exist already?
        configuration = client.sys.read_mount_configuration(path=name)
        current_state = configuration['data']
        exists = True
    except Exception:
        # doesn't exist
        pass

    # doesnt exist and should or does exist and shouldnt
    if (exists and state == 'disabled'):
        changed = True
    elif (not exists and state == 'enabled'):
        changed = True
    elif state == 'enabled':
        if 'version' in options:
            options['version'] = str(options['version'])

        if 'description' in current_state:
            if description != current_state['description']:
                changed = True
        if 'options' in current_state:
            current_options = current_state['options']
            for key in options.keys():
                if key not in current_options:
                    changed = True
                elif current_options[key] != options[key]:
                    changed = True
        elif options:
            changed = True
        for key in config.keys():
            if key not in current_state:
                changed = True
            elif current_state[key] != config[key]:
                changed = True
        if new_engine_configuration and not changed:
            engine_configuration = client.secrets.kv.read_configuration(name)['data']
            if cas_required is not None and engine_configuration.get('cas_required', None) != cas_required:
                changed = True
            elif max_versions is not None and engine_configuration.get('max_versions', None) != max_versions:
                changed = True
            else:
                new_engine_configuration = {}

    # create
    if changed and not exists and state == 'enabled' and not module.check_mode:
        if backend == 'kv':
            client.sys.enable_secrets_engine(backend, description=description, path=name, config=config,
                                             options=options)
            if new_engine_configuration:
                client.secrets.kv.v2.configure(mount_point=name, cas_required=cas_required, max_versions=max_versions)
        else:
            client.sys.enable_secrets_engine(backend, description=description, path=name, config=config)
        created = True

    # update
    elif changed and exists and state == 'enabled' and not module.check_mode:
        if backend == 'kv':
            client.sys.tune_mount_configuration(path=name, description=description, options=options, **config)
            if new_engine_configuration:
                client.secrets.kv.v2.configure(mount_point=name, cas_required=cas_required, max_versions=max_versions)
        else:
            client.sys.tune_mount_configuration(path=name, description=description, **config)

    # delete
    elif changed and state == 'disabled' and not module.check_mode:
        client.sys.disable_secrets_engine(path=name)

    return {'changed': changed, 'created': created}


if __name__ == '__main__':
    main()
