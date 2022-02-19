#!/usr/bin/env python
from hvac.exceptions import InvalidPath

from ansible.module_utils.hashivault import is_state_changed
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_secret
version_added: "0.1"
short_description: Hashicorp Vault write module
description:
    - Module to write to Hashicorp Vault.
options:
    state:
        description:
            - Update reads and overlays with values provided. Present reads and checks for changes and then overwrites
              with values provided. state of secret choices of present, update, or absent
    version:
        description:
            - version of the kv engine (int)
        default: 2
    mount_point:
        description:
            - secret mount point
        default: secret
    secret:
        description:
            - vault secret to write.
    data:
        description:
            - Keys and values to write.
    cas:
        description:
            - Check and set curent version 2 only
    permanent:
        description:
            - delete all versions and metadata for a given secret for kv engine version 2.
        default: false
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_secret:
        secret: giant
        data:
            foo: foe
            fie: fum
'''


def main():
    argspec = hashivault_argspec()
    argspec['state'] = dict(required=False, type='str', choices=['present', 'update', 'absent'],
                            default='present')
    argspec['version'] = dict(required=False, type='int', default=2)
    argspec['mount_point'] = dict(required=False, type='str', default='secret')
    argspec['secret'] = dict(required=True, type='str')
    argspec['data'] = dict(required=False, default={}, type='dict', no_log=True)
    argspec['cas'] = dict(required=False, type='int')
    argspec['permanent'] = dict(required=False, type='bool', default=False)
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_secret(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_secret(module):
    params = module.params
    client = hashivault_auth_client(params)
    state = params.get('state')
    version = params.get('version')
    mount_point = params.get('mount_point')
    secret = params.get('secret')
    data = params.get('data')
    cas = params.get('cas')
    permanent = params.get('permanent')

    if mount_point:
        secret_path = '%s/%s' % (mount_point, secret)
    else:
        secret_path = secret

    result = {"changed": False, "rc": 0}
    try:
        if version == 2:
            read_data = client.secrets.kv.v2.read_secret_version(secret, mount_point=mount_point)
            read_data = read_data.get('data', {})
        else:
            read_data = client.secrets.kv.v1.read_secret(secret, mount_point=mount_point)
        read_data = read_data.get('data', {})
    except InvalidPath:
        if state not in ['present', 'update']:
            result['msg'] = u"Secret %s nonexistent" % secret_path
            return result
        read_data = {}
    except Exception as e:
        result['rc'] = 1
        result['failed'] = True
        error_string = "%s(%s)" % (e.__class__.__name__, e)
        result['msg'] = u"Error %s reading %s" % (error_string, secret_path)
        return result

    if state == 'present' or state == 'update':
        if state == 'update':
            write_data = dict(read_data)
            write_data.update(data)
        else:
            write_data = data
        changed = is_state_changed(write_data, read_data)
        # result['write_data'] = write_data
        # result['read_data'] = read_data

        if not changed:
            result['msg'] = u"Secret %s unchanged" % secret_path
            return result
        if not module.check_mode:
            try:
                if version == 2:
                    client.secrets.kv.v2.create_or_update_secret(
                        mount_point=mount_point, cas=cas, path=secret, secret=write_data)
                else:
                    client.secrets.kv.v1.create_or_update_secret(
                        mount_point=mount_point, path=secret, secret=write_data)
            except Exception as e:
                result['rc'] = 1
                result['failed'] = True
                error_string = "%s(%s)" % (e.__class__.__name__, e)
                result['msg'] = u"Error %s writing %s" % (error_string, secret_path)
                return result

        result['msg'] = u"Secret %s written" % secret_path
        result['changed'] = True
    else:
        try:
            if version == 2:
                if permanent:
                    client.secrets.kv.v2.delete_metadata_and_all_versions(secret, mount_point=mount_point)
                else:
                    client.secrets.kv.v2.delete_latest_version_of_secret(secret, mount_point=mount_point)
            else:
                client.secrets.kv.v1.delete_secret(secret, mount_point=mount_point)
        except InvalidPath:
            result['msg'] = u"Secret %s nonexistent" % secret_path
            return result
        except Exception as e:
            result['rc'] = 1
            result['failed'] = True
            error_string = "%s(%s)" % (e.__class__.__name__, e)
            result['msg'] = u"Error %s deleting %s" % (error_string, secret_path)
            return result
        result['msg'] = u"Secret %s deleted" % secret_path
        result['changed'] = True
    return result


if __name__ == '__main__':
    main()
