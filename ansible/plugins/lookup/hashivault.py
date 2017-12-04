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
from urlparse import urljoin
import warnings

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.modules.hashivault import hashivault_read
from ansible.module_utils.hashivault import hashivault_default_token


class LookupModule(LookupBase):

    def get_url(self):
        url = os.getenv('VAULT_ADDR')
        if url:
            return url.rstrip('/')
        return "https://127.0.0.1:8200"


    def get_verify(self):
        capath = os.getenv('VAULT_CAPATH')
        if capath:
            return capath
        if os.getenv('VAULT_SKIP_VERIFY'):
            return False
        return True

    def run(self, terms, variables, **kwargs):
        path = terms[0]
        key = terms[1]
        token = hashivault_default_token()
        authtype = 'token'
        params = {
            'url': self.get_url(),
            'verify': self.get_verify(),
            'token': token,
            'authtype': 'token',
            'secret': path,
            'key': key,
        }
        result = hashivault_read.hashivault_read(params)

        if 'value' not in result:
            raise AnsibleError('Error reading vault %s/%s: %s\n%s' % (path, key, result.get('msg', 'msg not set'), result.get('stack_trace', '')))
        return [result['value']]


def main(argv=sys.argv[1:]):
    if len(argv) != 2:
        print("Usage: hashivault.py path key")
        return -1
    print LookupModule().run(argv, None)[0]
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
