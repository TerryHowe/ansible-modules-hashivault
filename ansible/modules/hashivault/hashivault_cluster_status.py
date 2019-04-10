#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_cluster_status
version_added: "3.16.4"
short_description: Hashicorp Vault cluster status module
description:
    - Module to get cluster status of Hashicorp Vault.
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
    standby_ok:
        description:
            - Specifies if being a standby should still return the active status code instead of the standby status code
        default: False
    method:
      description:
        - Method to use to get cluster status, supported methods are HEAD (produces 000 (empty body)) and GET (produces 000 application/json)
      default: HEAD
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_cluster_status:
      register: 'vault_cluster_status'
    - debug: msg="Cluster is initialized: {{vault_cluster_status.status.initialized}}"
'''


def main():
    argspec = hashivault_argspec()
    argspec['standby_ok'] = dict(required=False, type='bool', default=True)
    argspec['method'] = dict(required=False, default="HEAD")
    module = hashivault_init(argspec)
    result = hashivault_cluster_status(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_cluster_status(params):
    client = hashivault_client(params)
    response = client.sys.read_health_status(standby_ok=params.get("standby_ok"), method=params.get("method"))
    from requests.models import Response
    if isinstance(response, Response):
        try:
            status = response.json()
        except Exception:
            status = response.content
    else:
        status = response
    return {'status': status}


if __name__ == '__main__':
    main()
