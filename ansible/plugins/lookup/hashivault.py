#!/usr/bin/env python
#
# Vault Lookup Plugin
#
# A simple example of using the vault plugin in a role:
#    ---
#    - debug: msg="{{lookup('vault', 'ldapadmin', 'password')}}"
#
# The plugin must be run with VAULT_ADDR and VAULT_TOKEN set and
# exported.
#
# The plugin can be run manually for testing:
#     python ansible/plugins/lookup/hashivault.py ldapadmin password
#
import os
import sys

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

from ansible.module_utils.hashivault import (
    hashivault_default_token,
    hashivault_read,
)


class LookupModule(LookupBase):
    @staticmethod
    def _get_environment(environments, name, default_value=None):
        for env in environments:
            if name in env:
                return env.get(name)
        return os.getenv(name, default_value)

    def _get_url(self, environments):
        url = self._get_environment(environments, 'VAULT_ADDR')
        if url:
            return url.rstrip('/')
        return "https://127.0.0.1:8200"

    def _get_params(self, terms, environments, kwargs):
        path = terms[0]
        try:
            key = terms[1]
        except IndexError:
            key = None
        default = kwargs.get('default', None)
        version = kwargs.get('version')
        mount_point = kwargs.get('mount_point', 'secret')
        params = {
            'url': self._get_url(environments),
            'verify': self._get_verify(environments),
            'secret': path,
            'key': key,
            'default': default,
            'version': version,
            'mount_point': mount_point,
        }
        authtype = self._get_environment(environments, 'VAULT_AUTHTYPE', 'token')
        params['authtype'] = authtype
        login_mount_point = self._get_environment(environments, 'VAULT_LOGIN_MOUNT_POINT', authtype)
        params['login_mount_point'] = login_mount_point
        cacert = self._get_environment(environments, 'VAULT_CACERT')
        if cacert:
            params['ca_cert'] = cacert
        capath = self._get_environment(environments, 'VAULT_CAPATH')
        if capath:
            params['ca_path'] = capath
        params['client_cert'] = os.getenv('VAULT_CLIENT_CERT')
        params['client_key'] = os.getenv('VAULT_CLIENT_KEY')
        if authtype == 'approle':
            params['role_id'] = self._get_environment(environments, 'VAULT_ROLE_ID')
            params['secret_id'] = self._get_environment(environments, 'VAULT_SECRET_ID')
        elif authtype == 'userpass' or authtype == 'ldap':
            params['username'] = self._get_environment(environments, 'VAULT_USER')
            params['password'] = self._get_environment(environments, 'VAULT_PASSWORD')
        elif authtype == 'aws':
            params['aws_header'] = self._get_environment(environments, 'VAULT_AWS_HEADER')
        else:
            params['token'] = self._get_environment(environments, 'VAULT_TOKEN', hashivault_default_token())
        return params

    def _get_verify(self, environments):
        capath = self._get_environment(environments, 'VAULT_CAPATH')
        if capath:
            return capath
        cacert = self._get_environment(environments, 'VAULT_CACERT')
        if cacert:
            return cacert
        if self._get_environment(environments, 'VAULT_SKIP_VERIFY'):
            return False
        return True

    def run(self, terms, variables=None, **kwargs):
        environments = variables.get('environment', [])
        result = hashivault_read(self._get_params(terms, environments, kwargs))
        if 'value' not in result:
            path = terms[0]
            try:
                key = '/' + terms[1]
            except IndexError:
                key = ''
            raise AnsibleError('Error reading vault %s%s: %s\n%s' % (path, key, result.get('msg', 'msg not set'),
                                                                     result.get('stack_trace', '')))
        return [result['value']]


def main(argv=sys.argv[1:]):
    if len(argv) < 1:
        print("Usage: hashivault.py path [key]")
        return -1
    print(LookupModule().run(argv, {})[0])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
