#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
import json
from ast import literal_eval

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_db_secret_engine_role
version_added: "3.17.8"
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
        default: database
    name:
        description:
            - name of the role in vault
    state:
        description:
            - state of the object. choices: present, absent
        default: present
    token_ttl:
        description:
            - The TTL period of tokens issued using this role in seconds.
    token_max_ttl:
        description:
            - The maximum allowed lifetime of tokens issued in seconds using this role.
    role_file:
        description:
            - file with a json object containing play parameters. pass all params but name, state, mount_point which stay in the ansible play
    db_name:
        description:
            - name of the db configuration youre referencing. in my opinion, this should be called 'db connection' but hashi calls it db_name
    creation_statements:
        description:
            - "Specifies the database statements executed to create and configure a user. make sure your account for variables like this {{'{{name}}'}}"
    revocation_statements:
        description:
            - Specifies the database statements to be executed to revoke a user. See the plugin's API page for more information on support and formatting for this parameter.
    rollback_statements:
        description:
            - Specifies the database statements to be executed rollback a create operation in the event of an error. Not every plugin type will support this functionality. See the plugin's API page for more information on support and formatting for this parameter.
    renew_statements:
        description:
            - Specifies the database statements to be executed to renew a user. Not every plugin type will support this functionality. See the plugin's API page for more information on support and formatting for this parameter.
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
      hashivault_db_secret_engine_role:
        name: tester
        db_name: test
        creation_statements: []


    - hashivault_db_secret_engine_role:
        name: tester
        role_file: "/Users/dmullen/git/namespaces/test-args/azure/args-db-role-file.json"
        state: "present"
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['role_file'] = dict(required=False, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='database')
    argspec['token_ttl'] = dict(required=False, type='int', default=0)
    argspec['token_max_ttl'] = dict(required=False, type='int', default=0)
    argspec['creation_statements'] = dict(required=False, type='list', default=[])
    argspec['revocation_statements'] = dict(required=False, type='list', default=[])
    argspec['rollback_statements'] = dict(required=False, type='list', default=[])
    argspec['renew_statements'] = dict(required=False, type='list', default=[])
    argspec['db_name'] = dict(required=False, type='str')



    supports_check_mode=True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_db_secret_engine_role(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_db_secret_engine_role(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point')
    role_file = params.get('role_file')
    name = params.get('name')
    state = params.get('state')
    desired_state = dict()
    exists = False
    changed = False

    # do not want a trailing slash in name
    if name[-1] == '/':
        name = name.strip('/')
    if mount_point[-1]:
        mount_point = mount_point.strip('/')

    # if role_file is set, set desired_state to contents
    # else take values from ansible play
    if role_file:
        desired_state = json.loads(open(params.get('role_file'), 'r').read())
    else:
        desired_state['default_ttl'] = params.get('token_ttl')
        desired_state['max_ttl'] = params.get('token_max_ttl')
        desired_state['creation_statements'] = params.get('creation_statements')
        desired_state['revocation_statements'] = params.get('revocation_statements')
        desired_state['rollback_statements'] = params.get('rollback_statements')
        desired_state['db_name'] = params.get('db_name')

    # check if engine is enabled
    try:
        if (mount_point + "/") not in client.sys.list_mounted_secrets_engines()['data'].keys():
            return {'failed': True, 'msg': 'secret engine is not enabled', 'rc': 1}
    except:
        if module.check_mode:
            changed = True
        else:
            return {'failed': True, 'msg': 'secret engine is not enabled or namespace does not exist', 'rc': 1}

    # check if role exists
    try:
        client.secrets.database.read_role(name=name, mount_point=mount_point)
        # this role exists
        exists = True
    except Exception:
        # no roles exist yet
        pass

    if (exists and state == 'absent') or (not exists and state == 'present'):
        changed = True

    # compare current_state to desired_state
    if exists and state == 'present' and not changed:
        current_state = client.secrets.database.read_role(name=name, mount_point=mount_point)['data']
        for k, v in desired_state.items():
            if v != current_state[k]:
                changed = True
    elif exists and state == 'absent':
        changed = True

    # make the changes!

    if changed and state == 'present' and not module.check_mode:
        client.secrets.database.create_role(name=name, mount_point=mount_point, **desired_state)

    elif changed and state == 'absent' and not module.check_mode:
        client.secrets.database.delete_role(name=name, mount_point=mount_point)

    return {'changed': changed}


if __name__ == '__main__':
    main()
