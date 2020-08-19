#!/usr/bin/env python
import warnings

from hvac.exceptions import InvalidPath

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_write
version_added: "0.1"
short_description: Hashicorp Vault write module
description:
    - Module to write to Hashicorp Vault.
options:
    version:
        description:
            - version of the kv engine (int)
        default: 1
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
    alternate_data:
        description:
            - Keys and values to write. Use this if you need the returned data.
    cas:
        description:
            - Check and set curent version v2 only
    update:
        description:
            - This option is deprecated. Update the secret rather than overwrite. The module will read the secret and
              overlay with the data provided and write.
        default: False
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_write:
        secret: giant
        data:
            foo: foe
            fie: fum
'''


def main():
    argspec = hashivault_argspec()
    argspec['version'] = dict(required=False, type='int', default=1)
    argspec['mount_point'] = dict(required=False, type='str', default='secret')
    argspec['secret'] = dict(required=True, type='str')
    argspec['update'] = dict(required=False, default=False, type='bool')
    argspec['data'] = dict(required=False, default={}, type='dict', no_log=True)
    argspec['alternate_data'] = dict(required=False, default={}, type='dict')
    argspec['cas'] = dict(required=False, type='int')
    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_write(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def _convert_to_seconds(original_value):
    try:
        value = str(original_value)
        seconds = 0
        if 'h' in value:
            ray = value.split('h')
            seconds = int(ray.pop(0)) * 3600
            value = ''.join(ray)
        if 'm' in value:
            ray = value.split('m')
            seconds += int(ray.pop(0)) * 60
            value = ''.join(ray)
        if value:
            ray = value.split('s')
            seconds += int(ray.pop(0))
        return seconds
    except Exception:
        pass
    return original_value


def hashivault_changed(old_data, new_data):
    if sorted(old_data.keys()) != sorted(new_data.keys()):
        return True
    for key in old_data:
        old_value = old_data[key]
        new_value = new_data[key]
        if old_value == new_value:
            continue
        if key != 'ttl' and key != 'max_ttl':
            return True
        old_value = _convert_to_seconds(old_value)
        new_value = _convert_to_seconds(new_value)
        if old_value != new_value:
            return True
    return False


@hashiwrapper
def hashivault_write(module):
    result = {"changed": False, "rc": 0}
    params = module.params
    client = hashivault_auth_client(params)
    version = params.get('version')
    mount_point = params.get('mount_point')
    secret = params.get('secret')
    data = params.get('data')
    data = data or params.get('alternate_data')
    cas = params.get('cas')

    if secret.startswith('/'):
        secret = secret.lstrip('/')
        mount_point = ''
    if mount_point:
        secret_path = '%s/%s' % (mount_point, secret)
    else:
        secret_path = secret

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        changed = True
        write_data = data

        if params.get('update') or module.check_mode:
            # Do not move these reads outside of the update
            read_data = None
            try:
                if version == 2:
                    read_data = client.secrets.kv.v2.read_secret_version(secret, mount_point=mount_point)
                else:
                    read_data = client.read(secret_path) or {}
            except InvalidPath:
                read_data = None
            except Exception as e:
                result['rc'] = 1
                result['failed'] = True
                error_string = "%s(%s)" % (e.__class__.__name__, e)
                result['msg'] = u"Error %s reading %s" % (error_string, secret_path)
                return result
            if not read_data:
                read_data = {}
            read_data = read_data.get('data', {})

            if version == 2:
                read_data = read_data.get('data', {})

            write_data = dict(read_data)
            write_data.update(data)

            # result['write_data'] = write_data
            # result['read_data'] = read_data
            changed = hashivault_changed(read_data, write_data)

        if changed:
            if not module.check_mode:
                try:
                    if version == 2:
                        returned_data = client.secrets.kv.v2.create_or_update_secret(mount_point=mount_point, cas=cas,
                                                                                     path=secret, secret=write_data)
                    else:
                        returned_data = client.write(secret_path, **write_data)
                    if returned_data:
                        from requests.models import Response
                        if isinstance(returned_data, Response):
                            result['data'] = returned_data.text
                        else:
                            result['data'] = returned_data
                except Exception as e:
                    result['rc'] = 1
                    result['failed'] = True
                    error_string = "%s(%s)" % (e.__class__.__name__, e)
                    result['msg'] = u"Error %s writing %s" % (error_string, secret_path)
                    return result

            result['msg'] = u"Secret %s written" % secret_path
        result['changed'] = changed
    return result


if __name__ == '__main__':
    main()
