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
module: hashivault_delete
version_added: "3.4.0"
short_description: Hashicorp Vault delete module
description:
    - Module to delete from Hashicorp Vault.
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
            - secret to delete.
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_delete:
        secret: giant
'''


def main():
    argspec = hashivault_argspec()
    argspec['version'] = dict(required=False, type='int', default=1)
    argspec['mount_point'] = dict(required=False, type='str', default='secret')
    argspec['secret'] = dict(required=True, type='str')
    module = hashivault_init(argspec)
    result = hashivault_delete(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_delete(params):
    result = {"changed": False, "rc": 0}
    client = hashivault_auth_client(params)
    version = params.get('version')
    mount_point = params.get('mount_point')
    secret = params.get('secret')
    if secret.startswith('/'):
        secret = secret.lstrip('/')
        mount_point = ''
    if mount_point:
        secret_path = '%s/%s' % (mount_point, secret)
    else:
        secret_path = secret

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        returned_data = None
        try:
            if version == 2:
                returned_data = client.secrets.kv.v2.delete_latest_version_of_secret(secret, mount_point=mount_point)
            else:
                returned_data = client.delete(secret_path)
        except InvalidPath:
            pass
        except Exception as e:
            result['rc'] = 1
            result['failed'] = True
            error_string = "%s(%s)" % (e.__class__.__name__, e)
            result['msg'] = u"Error %s deleting %s" % (error_string, secret_path)
            return result
        if returned_data:
            result['data'] = returned_data.text
        result['msg'] = u"Secret %s deleted" % secret_path
    result['changed'] = True
    return result


if __name__ == '__main__':
    main()
