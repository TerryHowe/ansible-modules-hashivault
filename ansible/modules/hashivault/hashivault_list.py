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
      default this will list top-level keys under C(/secret), but you
      can provide an alternate location as I(secret).  This includes both
      immediate subkeys and subkey paths, like the C(vault list) command.
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
    secret:
        description:
            - 'secret path to list.  If this does not begin with a C(/)
              then it is interpreted as a subpath of C(/secret).  This
              is always interpreted as a "directory": if a key C(/secret/foo)
              exists, and you pass C(/secret/foo) as I(secret), then the key
              itself will not be returned, but subpaths like
              C(/secret/foo/bar) will.'
        default: ''
    version:
        description:
            - version of the kv engine (int)
        default: 1
    mount_point:
        description:
            - secret mount point
        default: secret
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
