#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_token_create
version_added: "3.3.0"
short_description: Hashicorp Vault token create module
description:
    - Module to create tokens in Hashicorp Vault.
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
            - "path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate : if ca_cert is specified, its value will take precedence"
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
            - "if set, do not verify presented TLS certificate before communicating with Vault server : setting this variable is not recommended except during testing"
        default: to environment variable VAULT_SKIP_VERIFY
    authtype:
        description:
            - "authentication type to use: token, userpass, github, ldap"
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
    password:
        description:
            - password to login to vault.
    role:
        description:
            - If set, the token will be created against the named role
    id:
        description:
            - The token value that clients will use to authenticate with vault
    policies:
        description:
            - List of Policy to associate with this token.
    metadata:
        description:
            - Metadata to associate with the token
    no_parent:
        description:
            - If specified, the token will have no parent
    lease:
        description:
            - If specified, the lease time will be this value. (e.g. 1h)
    display_name:
        description:
            - A display name to associate with this token
    num_uses:
        description:
            - The number of times this token can be used until it is automatically revoked
    no_default_policy:
        description:
            - If specified, the token will not have the "default" policy included in its policy set
        default: False
    ttl:
        description:
            - Initial TTL to associate with the token; renewals can extend this value.
    wrap_ttl:
        description:
            - Indicates that the response should be wrapped in a cubbyhole token with the requested TTL.
    orphan:
        description:
            - If specified, the token will have no parent. Only This prevents the new token from being revoked with your token.
    renewable:
        description:
            - Whether or not the token is renewable to extend its TTL up to Vault's configured maximum TTL for tokens
    explicit_max_ttl:
        description:
            - An explicit maximum lifetime for the token
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - name: "Create a {{admin_name}} token, and stop using root token"
      hashivault_token_create:
        display_name: "{{admin_name}}"
        policies: ["{{admin_name}}"]
        renewable: True
        token: "{{vault_root_token}}"
      register: "vault_token_admin"
'''


def main():
    argspec = hashivault_argspec()
    argspec['role'] = dict(required=False, type='str')
    argspec['id'] = dict(required=False, type='str')
    argspec['policies'] = dict(required=True, type='list')
    argspec['metadata'] = dict(required=False, type='str')
    argspec['no_parent'] = dict(required=False, type='bool', default=False)
    argspec['lease'] = dict(required=False, type='str')
    argspec['display_name'] = dict(required=True, type='str')
    argspec['num_uses'] = dict(required=False, type='str')
    argspec['no_default_policy'] = dict(required=False, type='bool', default=False)
    argspec['ttl'] = dict(required=False, type='str')
    argspec['wrap_ttl'] = dict(required=False, type='str')
    argspec['orphan'] = dict(required=False, type='bool', default=False)
    argspec['renewable'] = dict(required=False, type='bool')
    argspec['explicit_max_ttl'] = dict(required=False, type='str')
    module = hashivault_init(argspec)
    result = hashivault_token_create(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *


@hashiwrapper
def hashivault_token_create(params):
    client = hashivault_auth_client(params)
    role = params.get('role')
    id = params.get('id')
    policies = params.get('policies')
    metadata = params.get('metadata')
    no_parent = params.get('no_parent')
    lease = params.get('lease')
    display_name = params.get('display_name')
    num_uses = params.get('num_uses')
    no_default_policy = params.get('no_default_policy')
    ttl = params.get('ttl')
    wrap_ttl = params.get('wrap_ttl')
    orphan = params.get('orphan')
    renewable = params.get('renewable')
    explicit_max_ttl = params.get('explicit_max_ttl')

    token = client.create_token(
        role=role,
        id=id,
        policies=policies,
        meta=metadata,
        no_parent=no_parent,
        lease=lease,
        display_name=display_name,
        num_uses=num_uses,
        no_default_policy=no_default_policy,
        ttl=ttl,
        wrap_ttl=wrap_ttl,
        orphan=orphan,
        renewable=renewable,
        explicit_max_ttl=explicit_max_ttl
        )

    return {'changed': True, 'token': token}

if __name__ == '__main__':
    main()
