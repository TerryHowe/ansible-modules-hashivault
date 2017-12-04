import os
import warnings
from hvac import exceptions

import hvac
from ansible.module_utils.basic import AnsibleModule


def hashivault_argspec():
    argument_spec = dict(
        url = dict(required=False, default=os.environ.get('VAULT_ADDR', ''), type='str'),
        ca_cert = dict(required=False, default=os.environ.get('VAULT_CACERT', ''), type='str'),
        ca_path = dict(required=False, default=os.environ.get('VAULT_CAPATH', ''), type='str'),
        client_cert = dict(required=False, default=os.environ.get('VAULT_CLIENT_CERT', ''), type='str'),
        client_key = dict(required=False, default=os.environ.get('VAULT_CLIENT_KEY', ''), type='str'),
        verify = dict(required=False, default=(not os.environ.get('VAULT_SKIP_VERIFY', '')), type='bool'),
        authtype = dict(required=False, default=os.environ.get('VAULT_AUTHTYPE', 'token'), type='str'),
        token = dict(required=False, default=hashivault_default_token(), type='str', no_log=True),
        username = dict(required=False, type='str'),
        password = dict(required=False, type='str',no_log=True),
        role_id = dict(required=False, default=os.environ.get('VAULT_ROLE_ID', ''), type='str', no_log=True),
        secret_id = dict(required=False, default=os.environ.get('VAULT_SECRET_ID', ''), type='str', no_log=True)
    )
    return argument_spec


def hashivault_init(argument_spec):
    return AnsibleModule(argument_spec=argument_spec)


def hashivault_client(params):
    url = params.get('url')
    ca_cert = params.get('ca_cert')
    ca_path = params.get('ca_path')
    client_cert = params.get('client_cert')
    client_key = params.get('client_key')
    cert = (client_cert, client_key)
    check_verify = params.get('verify')
    if check_verify == '' or check_verify:
        if ca_cert:
            verify = ca_cert
        elif ca_path:
            verify = ca_path
        else:
            verify = check_verify
    else:
        verify = check_verify
    client = hvac.Client(url=url, cert=cert, verify=verify)
    return client


def hashivault_auth(client, params):
    token = params.get('token')
    authtype = params.get('authtype')
    username = params.get('username')
    password = params.get('password')
    secret_id = params.get('secret_id')
    role_id = params.get('role_id')

    if authtype == 'github':
        client.auth_github(token)
    elif authtype == 'userpass':
        client.auth_userpass(username, password)
    elif authtype == 'ldap':
        client.auth_ldap(username, password)
    elif authtype == 'approle':
        client = AppRoleClient(client,role_id,secret_id)
    else:
        client.token = token
    return client


def hashivault_auth_client(params):
    client = hashivault_client(params)
    return hashivault_auth(client, params)


def hashiwrapper(function):
    def wrapper(*args, **kwargs):
        result = { "changed": False, "rc" : 0}
        try:
            result.update(function(*args, **kwargs))
        except Exception as e:
            result['rc'] = 1
            result['failed'] = True
            result['msg'] = "Exception: " + str(e)
        return result
    return wrapper


def hashivault_default_token():
    """Get a default Vault token from an environment variable or a file."""
    if 'VAULT_TOKEN' in os.environ:
        return os.environ['VAULT_TOKEN']
    token_file = os.path.expanduser('~/.vault-token')
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return f.read()
    return ''


class AppRoleClient(object):
    """
    hvac.Client decorator which generates and sets a new approle token on every
    function call. This allows multiple calls to Vault without having to manually
    generate and set a token on every Vault call.
    """

    def __init__(self, client, role_id, secret_id):
        object.__setattr__(self,'client',client)
        object.__setattr__(self,'role_id',role_id)
        object.__setattr__(self,'secret_id',secret_id)


    def __setattr__(self,name,val):
        """
        sets attribute in decorated class (Client)
        """
        client = object.__getattribute__(self,'client')
        client.__setattr__(name,val)


    def __getattribute__ (self,name):
        """
        generates and sets new approle token in decorated class (Client)
        returns decorated class (Client) attribute
        """
        client = object.__getattribute__(self,'client')
        attr = client.__getattribute__(name)
        if (callable(attr)):
            role_id = object.__getattribute__(self,'role_id')
            secret_id = object.__getattribute__(self,'secret_id')
            resp = client.auth_approle(role_id,secret_id)
            client.token = str(resp['auth']['client_token'])
        return attr