#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
from ansible.module_utils.hashivault import get_keys_updated
from hvac.exceptions import InvalidPath

ANSIBLE_METADATA = {'status': ['stableinterface'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = '''
---
module: hashivault_k8s_auth_config
version_added: "4.3.0"
short_description: Hashicorp Vault k8s auth config
description:
    - Module to configure an k8s auth mount
options:
    mount_point:
        description:
            - name of the secret engine mount name.
        default: kubernetes
    kubernetes_host:
        description:
            - host must be a host string, a host:port pair, or a URL to the base of the Kubernetes API server
    token_reviewer_jwt:
        description:
            -  a service account JWT used to access the TokenReview API to validate other JWTs during login
    kubernetes_ca_cert:
        description:
            - PEM encoded CA cert for use by the TLS client used to talk with the Kubernetes API
    pem_keys:
        description:
            - Optional list of PEM-formatted public keys or certificates used to verify the signatures of Kubernetes
              service account JWTs. If a certificate is given, its public key will be extracted.
    issuer:
        description:
            - Optional JWT issuer. If no issuer is specified, then this plugin will use kubernetes.io/serviceaccount as
              the default issuer (Available in hvac 0.10.2).
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_k8s_auth_config:
        kubernetes_host: https://192.168.99.100:8443
        kubernetes_ca_cert: "-----BEGIN CERTIFICATE-----\n.....\n-----END CERTIFICATE-----"
'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='kubernetes')
    argspec['kubernetes_host'] = dict(required=False, type='str', default=None)
    argspec['token_reviewer_jwt'] = dict(required=False, type='str', default=None)
    argspec['kubernetes_ca_cert'] = dict(required=False, type='str', default=None)
    argspec['pem_keys'] = dict(required=False, type='list', default=None)
    argspec['issuer'] = dict(required=False, type='str', default=None)
    required_together = [['kubernetes_host', 'kubernetes_ca_cert']]

    module = hashivault_init(argspec, supports_check_mode=True, required_together=required_together)
    result = hashivault_k8s_auth_config(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_k8s_auth_config(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point').strip('/')

    desired_state = dict()
    desired_state['kubernetes_host'] = params.get('kubernetes_host')
    desired_state['token_reviewer_jwt'] = params.get('token_reviewer_jwt')
    desired_state['kubernetes_ca_cert'] = params.get('kubernetes_ca_cert')
    desired_state['pem_keys'] = params.get('pem_keys')
    if params.get('issuer'):
        desired_state['issuer'] = params.get('issuer')
    desired_state['mount_point'] = mount_point

    keys_updated = desired_state.keys()
    try:
        current_state = client.auth.kubernetes.read_config(mount_point=mount_point)
        keys_updated = get_keys_updated(current_state, desired_state)
        if not keys_updated:
            return {'changed': False}
    except InvalidPath:
        pass

    if not module.check_mode:
        client.auth.kubernetes.configure(**desired_state)
    return {'changed': True, 'keys_updated': keys_updated}


if __name__ == '__main__':
    main()
