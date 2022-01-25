#!/usr/bin/env python
from hvac.exceptions import InvalidPath

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
        secret = secret.replace('metadata/', '', 1)
        version = 2
        metadata = True
    else:
        metadata = False

    try:
        if version == 2:
            if secret and metadata:
                response = client.secrets.kv.v2.read_secret_metadata(path=secret, mount_point=mount_point)
                result['metadata'] = response.get('data', {})
            else:
                response = client.secrets.kv.v2.list_secrets(path=secret, mount_point=mount_point)
                result['secrets'] = response.get('data', {}).get('keys', [])
        else:
            response = client.secrets.kv.v1.list_secrets(path=secret, mount_point=mount_point)
            result['secrets'] = response.get('data', {}).get('keys', [])
    except InvalidPath:
        secret_path = mount_point
        if secret:
            secret_path += '/' + secret
        return {'failed': True, 'rc': 1, 'msg': 'Secret does not exist: ' + secret_path}
    except Exception as e:
        return {'failed': True, 'rc': 1, 'msg': str(e)}
    return result


if __name__ == '__main__':
    main()
