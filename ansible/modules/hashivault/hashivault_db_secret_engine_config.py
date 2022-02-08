#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_db_secret_engine_config
version_added: "3.17.8"
short_description: Hashicorp Vault database secrets engine config
description:
    - Module to configure a database secrets engine
options:
    mount_point:
        description:
            - name of the secret engine mount name.
        default: database
    state:
        description:
            - should configuration be present or absent
        default: present
    config_file:
        description:
            - Optional location of file containing relevant db configuration info. use either this or the following
              ansible params in your play
    connection_details:
        description:
            - root level database credential for example username, password, connection_url.
    plugin_name:
        description:
            - name of database plugin used. see out of the box list at
              https://www.vaultproject.io/docs/secrets/databases/index.html
    allowed_roles:
        description:
            - list of the roles allowed to use this connection. Defaults to empty (no roles), if contains a "*" any role
              can use this connection.
        default: []
    verify_connection:
        description:
            - Specifies if the connection is verified during initial configuration. Defaults to true.
        default: true
    root_credentials_rotate_statements:
        description:
            - Specifies the database statements to be executed to rotate the root user's credentials. See the plugin's
              API page for more information on support and formatting for this parameter.
        default: []
        aliases: [ root_rotation_statements ]
    password_policy:
        description:
            - The name of the password policy to use when generating passwords for this database. If not specified,
              this will use a default policy defined as 20 characters with at least 1 uppercase, 1 lowercase, 1 number,
              and 1 dash character.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_db_secret_engine_config:
        name: test
        plugin_name: "postgresql-database-plugin" #https://www.vaultproject.io/docs/secrets/databases/index.html
        allowed_roles: ["my-role"]
        connection_details:
            username: "myuser@dbname"
            password: "P@ssw0rd"
            connection_url: "postgresql://{{'{{username}}'}}:{{'{{password}}'}}@blergh-db.com:5230"
        state: "present

    - hashivault_db_secret_engine_config:
        name: test
        config_file: /users/drewbuntu/my-db-config.json
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['mount_point'] = dict(required=False, type='str', default='database')
    argspec['config_file'] = dict(required=False, type='str', default=None)
    argspec['plugin_name'] = dict(required=False, type='str')
    argspec['allowed_roles'] = dict(required=False, type='list', default=[])
    argspec['root_credentials_rotate_statements'] = dict(required=False, type='list',
                                                         aliases=['root_rotation_statements'], default=[])
    argspec['verify_connection'] = dict(required=False, type='bool', default=True)
    argspec['connection_details'] = dict(required=True, type='dict', no_log=True)
    argspec['password_policy'] = dict(required=False, type='str', no_log=True, default='')
    required_one_of = [['config_file', 'connection_details']]

    module = hashivault_init(argspec, supports_check_mode=True, required_one_of=required_one_of)
    result = hashivault_db_secret_engine_config(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_db_secret_engine_config(module):
    params = module.params
    client = hashivault_auth_client(params)
    config_file = params.get('config_file')
    mount_point = params.get('mount_point').strip('/')
    state = params.get('state')
    name = params.get('name')
    desired_state = dict()

    # if config_file is set value from file
    # else set from passed args
    if config_file:
        desired_state = json.loads(open(params.get('config_file'), 'r').read())
    else:
        desired_state['plugin_name'] = params.get('plugin_name')
        desired_state['allowed_roles'] = params.get('allowed_roles')
        desired_state['verify_connection'] = params.get('verify_connection')
        desired_state['password_policy'] = params.get('password_policy')
        desired_state['root_rotation_statements'] = params.get('root_credentials_rotate_statements')
        connection_details = params.get('connection_details')
        desired_state.update(connection_details)
        del connection_details["password"]

    # not a required param but must ensure a value for current vs desired object comparison
    if 'root_rotation_statements' not in desired_state:
        desired_state['root_rotation_statements'] = []

    exists = False
    current_state = {}
    try:
        current_state = client.secrets.database.read_connection(name=name, mount_point=mount_point)
        exists = True
    except Exception:
        # does not exist
        pass

    changed = False
    if exists:
        if state == 'absent':
            changed = True
        else:
            for k, v in current_state.get('data', {}).items():
                # connection_url is passed as a nested item
                if k == 'connection_details':
                    if v['username'] != desired_state['username']:
                        changed = True
                    if v['connection_url'] != desired_state['connection_url']:
                        changed = True
                elif k == 'root_credentials_rotate_statements':
                    if v != desired_state['root_rotation_statements']:
                        changed = True
                elif v != desired_state[k]:
                    changed = True
    elif state == 'present':
        changed = True

    # if configs dont match and checkmode is off, complete the change
    if changed and state == 'present' and not module.check_mode:
        client.secrets.database.configure(name=name, mount_point=mount_point, **desired_state)
    elif changed and state == 'absent' and not module.check_mode:
        client.secrets.database.delete_connection(name=name, mount_point=mount_point)

    return {'changed': changed}


if __name__ == '__main__':
    main()
