import os
import warnings

import hvac
import requests
from ansible.module_utils.basic import AnsibleModule, env_fallback
from hvac.exceptions import InvalidPath


def hashivault_argspec():
    argument_spec = dict(
        url=dict(required=False, default=os.environ.get('VAULT_ADDR', ''), type='str'),
        ca_cert=dict(required=False, default=os.environ.get('VAULT_CACERT', ''), type='str'),
        ca_path=dict(required=False, default=os.environ.get('VAULT_CAPATH', ''), type='str'),
        client_cert=dict(required=False, default=os.environ.get('VAULT_CLIENT_CERT', ''), type='str'),
        client_key=dict(required=False, default=os.environ.get('VAULT_CLIENT_KEY', ''), type='str'),
        verify=dict(required=False, default=(not os.environ.get('VAULT_SKIP_VERIFY', '')), type='bool'),
        authtype=dict(required=False, default=os.environ.get('VAULT_AUTHTYPE', 'token'), type='str'),
        login_mount_point=dict(required=False, default=os.environ.get('VAULT_LOGIN_MOUNT_POINT', None), type='str'),
        token=dict(required=False, fallback=(hashivault_default_token, ''), type='str', no_log=True),
        username=dict(required=False, default=os.environ.get('VAULT_USER', ''), type='str'),
        password=dict(required=False, fallback=(env_fallback, ['VAULT_PASSWORD']), type='str', no_log=True),
        role_id=dict(required=False, fallback=(env_fallback, ['VAULT_ROLE_ID']), type='str', no_log=True),
        secret_id=dict(required=False, fallback=(env_fallback, ['VAULT_SECRET_ID']), type='str', no_log=True),
        aws_header=dict(required=False, fallback=(env_fallback, ['VAULT_AWS_HEADER']), type='str', no_log=True),
        namespace=dict(required=False, default=os.environ.get('VAULT_NAMESPACE', None), type='str')
    )
    return argument_spec


def hashivault_init(argument_spec, supports_check_mode=False, required_if=None, required_together=None,
                    required_one_of=None, mutually_exclusive=None):
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=supports_check_mode,
                           required_if=required_if, required_together=required_together,
                           required_one_of=required_one_of, mutually_exclusive=mutually_exclusive)
    module.no_log_values.discard("0")
    module.no_log_values.discard(0)
    module.no_log_values.discard("1")
    module.no_log_values.discard(1)
    module.no_log_values.discard(True)
    module.no_log_values.discard(False)
    return module


def get_ec2_iam_role():
    request = requests.get(url='http://169.254.169.254/latest/meta-data/iam/security-credentials/')
    request.raise_for_status()
    return request.content


def get_ec2_iam_credentials(header_value, role_id):
    role_name = get_ec2_iam_role()
    metadata_url = 'http://169.254.169.254/latest/meta-data/iam/security-credentials/{role}'.format(
        role=role_name
    )
    response = requests.get(url=metadata_url)
    response.raise_for_status()
    credentials = response.json()
    return dict(
        access_key=credentials['AccessKeyId'],
        secret_key=credentials['SecretAccessKey'],
        session_token=credentials['Token'],
        header_value=header_value,
        role=role_id
    )


def hashivault_client(params):
    url = params.get('url')
    ca_cert = params.get('ca_cert')
    ca_path = params.get('ca_path')
    client_cert = params.get('client_cert')
    client_key = params.get('client_key')
    cert = (client_cert, client_key)
    check_verify = params.get('verify')
    namespace = params.get('namespace', None)
    if check_verify == '' or check_verify:
        if ca_cert:
            verify = ca_cert
        elif ca_path:
            verify = ca_path
        else:
            verify = check_verify
    else:
        verify = check_verify
    client = hvac.Client(url=url, cert=cert, verify=verify, namespace=namespace)
    return client


def hashivault_auth(client, params):
    token = params.get('token')
    authtype = params.get('authtype')
    login_mount_point = params.get('login_mount_point', authtype)
    if not login_mount_point:
        login_mount_point = authtype
    username = params.get('username')
    password = params.get('password')
    secret_id = params.get('secret_id')
    role_id = params.get('role_id')

    if authtype == 'github':
        client.auth.github.login(token, mount_point=login_mount_point)
    elif authtype == 'userpass':
        client.auth_userpass(username, password, mount_point=login_mount_point)
    elif authtype == 'ldap':
        client.auth.ldap.login(username, password, mount_point=login_mount_point)
    elif authtype == 'approle':
        client = AppRoleClient(client, role_id, secret_id, mount_point=login_mount_point)
    elif authtype == 'tls':
        client.auth_tls()
    elif authtype == 'aws':
        credentials = get_ec2_iam_credentials(params.get['aws_header'], role_id)
        client.auth_aws_iam(**credentials)
    else:
        client.token = token
    return client


def hashivault_auth_client(params):
    client = hashivault_client(params)
    return hashivault_auth(client, params)


def hashiwrapper(function):
    def wrapper(*args, **kwargs):
        result = {"changed": False, "rc": 0}
        result.update(function(*args, **kwargs))
        return result
    return wrapper


def hashivault_default_token():
    """Get a default Vault token from an environment variable or a file."""
    if 'VAULT_TOKEN' in os.environ:
        return os.environ['VAULT_TOKEN']
    token_file = os.path.expanduser('~/.vault-token')
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return f.read().strip()
    return ''


@hashiwrapper
def hashivault_read(params):
    result = {"changed": False, "rc": 0}
    client = hashivault_auth_client(params)
    version = params.get('version')
    mount_point = params.get('mount_point')
    secret = params.get('secret')

    key = params.get('key')
    default = params.get('default')
    if secret.startswith('/'):
        secret = secret.lstrip('/')
        mount_point = ''
    if mount_point:
        secret_path = '%s/%s' % (mount_point, secret)
    else:
        secret_path = secret

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            if version == 2:
                response = client.secrets.kv.v2.read_secret_version(secret, mount_point=mount_point)
            else:
                response = client.read(secret_path)
        except InvalidPath:
            response = None
        except Exception as e:
            result['rc'] = 1
            result['failed'] = True
            error_string = "%s(%s)" % (e.__class__.__name__, e)
            result['msg'] = u"Error %s reading %s" % (error_string, secret_path)
            return result
        if not response:
            if default is not None:
                result['value'] = default
                return result
            result['rc'] = 1
            result['failed'] = True
            result['msg'] = u"Secret %s is not in vault" % secret_path
            return result
        if version == 2:
            try:
                data = response.get('data', {})
                data = data.get('data', {})
            except Exception:
                data = str(response)
        else:
            data = response['data']
        lease_duration = response.get('lease_duration', None)
        if lease_duration is not None:
            result['lease_duration'] = lease_duration
        lease_id = response.get('lease_id', None)
        if lease_id is not None:
            result['lease_id'] = lease_id
        renewable = response.get('renewable', None)
        if renewable is not None:
            result['renewable'] = renewable
        wrap_info = response.get('wrap_info', None)
        if wrap_info is not None:
            result['wrap_info'] = wrap_info
    if key and key not in data:
        if default is not None:
            result['value'] = default
            return result
        result['rc'] = 1
        result['failed'] = True
        result['msg'] = u"Key %s is not in secret %s" % (key, secret_path)
        return result
    if key:
        value = data[key]
    else:
        value = data
    result['value'] = value
    return result


class AppRoleClient(object):
    """
    hvac.Client decorator which generates and sets a new approle token on every
    function call. This allows multiple calls to Vault without having to manually
    generate and set a token on every Vault call.
    """

    def __init__(self, client, role_id, secret_id, mount_point):
        object.__setattr__(self, 'client', client)
        object.__setattr__(self, 'role_id', role_id)
        object.__setattr__(self, 'secret_id', secret_id)
        object.__setattr__(self, 'login_mount_point', mount_point)

    def __setattr__(self, name, val):
        """
        sets attribute in decorated class (Client)
        """
        client = object.__getattribute__(self, 'client')
        client.__setattr__(name, val)

    def __getattribute__(self, name):
        """
        generates and sets new approle token in decorated class (Client)
        returns decorated class (Client) attribute
        """
        client = object.__getattribute__(self, 'client')
        attr = client.__getattribute__(name)

        role_id = object.__getattribute__(self, 'role_id')
        secret_id = object.__getattribute__(self, 'secret_id')
        login_mount_point = object.__getattribute__(self, 'login_mount_point')
        resp = client.auth_approle(role_id, secret_id=secret_id, mount_point=login_mount_point)
        client.token = str(resp['auth']['client_token'])
        return attr


def check_secrets_engines(module, client):
    """Checks if secrets engine is mounted

    :param module: Ansible module. Must contain mount_point in parameters.
    :param mounted: HVAC client
    :return: change status, error
    :rtype: (bool, dict)
    """
    changed = False
    err = None
    try:
        if (module.params.get('mount_point') + "/") not in client.sys.list_mounted_secrets_engines()['data'].keys():
            err = {'failed': True, 'msg': 'secret engine is not enabled', 'rc': 1}
    except Exception:
        if module.check_mode:
            changed = True
        else:
            err = {'failed': True, 'msg': 'secret engine is not enabled or namespace does not exist', 'rc': 1}
    return changed, err


def check_auth_methods(module, client):
    """Checks if auth engine is mounted

    :param module: Ansible module. Must contain mount_point in parameters.
    :param mounted: HVAC client
    :return: change status, error
    :rtype: (bool, dict)
    """
    changed = False
    err = None
    try:
        if (module.params.get('mount_point') + "/") not in client.sys.list_auth_methods()['data'].keys():
            err = {'failed': True, 'msg': 'auth method is not enabled', 'rc': 1}
    except Exception:
        if module.check_mode:
            changed = True
        else:
            err = {'failed': True, 'msg': 'auth mount is not enabled or namespace does not exist', 'rc': 1}

    return changed, err


def check_pki_role(name, mount_point, client):
    """Checks if role is prtesent in secrets engine

    :param module: Ansible module. Must contain mount_point in parameters.
    :param mounted: HVAC client
    :return: change status, error
    :rtype: (bool, dict)
    """
    try:
        return client.secrets.pki.read_role(name=name, mount_point=mount_point).get('data')
    except Exception:
        return None


def compare_state(desired_state, current_state, ignore=None):
    """Compares desired state to current state. Returns true if objects are equal

    Recursively walks dict object to compare all keys

    :param desired_state: The state user desires.
    :param current_state: The state that currently exists.
    :param ignore: Ignore these keys.
    :type ignore: list

    :return: True if the states are the same.
    :rtype: bool
    """

    if ignore is None:
        ignore = []
    if (type(desired_state) is list):
        if ((type(current_state) != list) or (len(desired_state) != len(current_state))):
            return False
        return set(desired_state) == set(current_state)

    if (type(desired_state) is dict):
        if (type(current_state) != dict):
            return False

        # iterate over dictionary keys
        for key in desired_state.keys():
            if key in ignore:
                continue
            v = desired_state[key]
            if ((key not in current_state) or (not compare_state(v, current_state.get(key)))):
                return False
        return True

    # lots of things get handled as strings in ansible that aren't necessarily strings, can extend this list later.
    if isinstance(desired_state, str) and isinstance(current_state, int):
        current_state = str(current_state)

    return ((desired_state == current_state))


def get_keys_updated(desired_state, current_state, ignore=None):
    """Return list of keys that have different values

    Recursively walks dict object to compare all keys

    :param desired_state: The state user desires.
    :type desired_state: dict
    :param current_state: The state that currently exists.
    :type current_state: dict
    :param ignore: Ignore these keys.
    :type ignore: list

    :return: Different items
    :rtype: list
    """

    if ignore is None:
        ignore = []

    differences = []
    for key in desired_state.keys():
        if key in ignore:
            continue
        v = desired_state[key]
        if ((key not in current_state) or (not compare_state(v, current_state.get(key)))):
            differences.append(key)
    return differences
