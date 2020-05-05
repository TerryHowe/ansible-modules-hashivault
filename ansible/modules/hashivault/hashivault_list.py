#!/usr/bin/env python
import warnings

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_list
version_added: "2.9"
short_description: Hashicorp Vault list
description:
    - The M(hashivault_list) module lists keys in Hashicorp Vault.  By
      default this will list top-level keys under `/secret`, but you
      can provide an alternate location as *secret*.  This includes both
      immediate subkeys and subkey paths, like the `vault list` command.
options:
    secret:
        description:
            - 'secret path to list.  If this does not begin with a `/`
              then it is interpreted as a subpath of `/secret`.  This
              is always interpreted as a "directory": if a key `/secret/foo`
              exists, and you pass `/secret/foo` as *secret*, then the key
              itself will not be returned, but subpaths like
              `/secret/foo/bar` will.'
        default: ''
    version:
        description:
            - version of the kv engine (int)
        default: 1
    mount_point:
        description:
            - secret mount point
        default: secret
extends_documentation_fragment: hashivault
'''
RETURN = '''
---
secrets:
    description: list of secrets found, if any
    returned: success
    type: list
    sample: ["giant", "stalks/"]
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_list:
        secret: 'giant'
        version: 2
      register: 'fie'
    - debug: msg="Known secrets are {{ fie.secrets|join(', ') }}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['version'] = dict(required=False, type='int', default=1)
    argspec['mount_point'] = dict(required=False, type='str', default='secret')
    argspec['secret'] = dict(default='', type='str')
    module = hashivault_init(argspec)
    result = hashivault_list(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_list(params):
    result = {"changed": False, "rc": 0}
    client = hashivault_auth_client(params)
    version = params.get('version')
    mount_point = params.get('mount_point')
    secret = params.get('secret')

    if secret.startswith('/'):
        secret = secret.lstrip('/')
        listo = secret.split('/')
        if listo:
            mount_point = next(iter(listo), mount_point)
            secret = '/'.join(listo[1:])
    # for backwards compatibiltiy with old hashivault_list module
    if secret.startswith('metadata/'):
        version = 2
        secret = secret.lstrip('metadata/')

    response = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            if version == 2:
                response = client.secrets.kv.v2.list_secrets(path=secret, mount_point=mount_point)
            else:
                response = client.secrets.kv.v1.list_secrets(path=secret, mount_point=mount_point)
        except Exception as e:
            if response is None:
                response = {}
            else:
                return {'failed': True, 'msg': str(e)}
        result['secrets'] = response.get('data', {}).get('keys', [])
    return result


if __name__ == '__main__':
    main()
