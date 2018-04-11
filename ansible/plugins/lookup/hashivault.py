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
import json
import os
import requests
import sys
import warnings

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.modules.hashivault import hashivault_read
from ansible.module_utils.hashivault import hashivault_default_token


class LookupModule(LookupBase):

    def _get_url(self):
        url = os.getenv('VAULT_ADDR')
        if url:
            return url.rstrip('/')
        return "https://127.0.0.1:8200"

    def _get_params(self, terms, kwargs):
        path = terms[0]
        try:
            key = terms[1]
        except IndexError:
            key = None
        default = kwargs.get('default', None)
        params = {
            'url': self._get_url(),
            'verify': self._get_verify(),
            'secret': path,
            'key': key,
            'default': default,
        }
        authtype = os.getenv('VAULT_AUTHTYPE', 'token')
        params['authtype'] = authtype
        if authtype == 'approle':
            params['role_id'] = os.getenv('VAULT_ROLE_ID')
            params['secret_id'] = os.getenv('VAULT_SECRET_ID')
        elif authtype == 'userpass' or authtype == 'ldap':
            params['username'] = os.getenv('VAULT_USER')
            params['password'] = os.getenv('VAULT_PASSWORD')
        else:
            params['token'] = hashivault_default_token()

        return params

    def _get_verify(self):
        capath = os.getenv('VAULT_CAPATH')
        if capath:
            return capath
        if os.getenv('VAULT_SKIP_VERIFY'):
            return False
        return True

    def run(self, terms, variables, **kwargs):
        result = hashivault_read.hashivault_read(self._get_params(terms, kwargs))
        if 'value' not in result:
            path = terms[0]
            try:
                key = '/' + terms[1]
            except IndexError:
                key = ''
            raise AnsibleError('Error reading vault %s%s: %s\n%s' % (path, key, result.get('msg', 'msg not set'), result.get('stack_trace', '')))
        return [result['value']]


def main(argv=sys.argv[1:]):
    if len(argv) < 1:
        print("Usage: hashivault.py path [key]")
        return -1
    print(LookupModule().run(argv, None)[0])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
