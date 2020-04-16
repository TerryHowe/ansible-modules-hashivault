#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

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
extends_documentation_fragment: hashivault
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_k8s_auth_config:
        kubernetes_host: ""
        kubernetes_ca_cert: ""
        token_reviewer_jwt: ""

'''


def main():
    argspec = hashivault_argspec()
    argspec['mount_point'] = dict(required=False, type='str', default='kubernetes')
    argspec['kubernetes_host'] = dict(required=False, type='str', default=None)
    argspec['token_reviewer_jwt'] = dict(required=False, type='str', default=None)
    argspec['kubernetes_ca_cert'] = dict(required=False, type='str', default=None)

    supports_check_mode = True
    required_together = [['kubernetes_host', 'kubernetes_ca_cert', 'token_reviewer_jwt']]

    module = hashivault_init(argspec, supports_check_mode, required_together)
    result = hashivault_k8s_auth_config(module)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_k8s_auth_config(module):
    params = module.params
    client = hashivault_auth_client(params)
    mount_point = params.get('mount_point')
    if mount_point[-1]:
        mount_point = mount_point.strip('/')

    desired_state = dict()
    desired_state['kubernetes_host'] = params.get('kubernetes_host')
    desired_state['token_reviewer_jwt'] = params.get('token_reviewer_jwt')
    desired_state['kubernetes_ca_cert'] = params.get('kubernetes_ca_cert')
    desired_state['mount_point'] = mount_point

    # check if engine is enabled
    try:
        if (mount_point + "/") not in client.sys.list_auth_methods():
            return {'failed': True, 'msg': (mount_point + ' auth metod not enabled'), 'rc': 1}
    except:
        return {'failed': True, 'msg': (mount_point + ' error getting auth method'), 'rc': 1}

    if not module.check_mode:
        client.auth.kubernetes.configure(**desired_state)

    return {'changed': True}


if __name__ == '__main__':
    main()
