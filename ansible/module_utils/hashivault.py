import os
import warnings

import hvac
from ansible.module_utils.basic import AnsibleModule


def hashivault_argspec():
    argument_spec = dict(
        url = dict(required=False, default=os.environ.get('VAULT_ADDR', ''), type='str'),
        verify = dict(required=False, default=(not os.environ.get('VAULT_SKIP_VERIFY', '')), type='bool'),
        authtype = dict(required=False, default='token', type='str'),
        token = dict(required=False, default=os.environ.get('VAULT_TOKEN', ''), type='str'),
        username = dict(required=False, type='str'),
        password = dict(required=False, type='str')
    )
    return argument_spec


def hashivault_init(argument_spec):
    return AnsibleModule(argument_spec=argument_spec)


def hashivault_client(params):
    url = params.get('url')
    verify = params.get('verify')
    token = params.get('token')
    authtype = params.get('authtype')
    token = params.get('token')
    username = params.get('username')
    password = params.get('password')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        client = hvac.Client(url=url, verify=verify)
        if authtype == 'github':
            client.auth_github(token)
        elif authtype == 'userpass':
            client.auth_userpass(username, password)
        elif authtype == 'ldap':
            client.auth_ldap(username, password)
        else:
            client.token = token
    return client


def hashiwrapper(function):
    def wrapper(*args, **kwargs):
        result = { "changed": False, "rc" : 0}
        try:
            result.update(function(*args, **kwargs))
        except Exception as e:
            import traceback
            result['rc'] = 1
            result['failed'] = True
            result['msg'] = "Exception: " + str(e)
            result['stack_trace'] = traceback.format_exc()
        return result
    return wrapper
