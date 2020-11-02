#!/usr/bin/env python
#
# Vault Lookup Plugin
#
# A simple example of using the vault plugin in a role:
#    ---
#    - debug: msg="{{lookup('vault', 'ldapadmin', 'password', mount_point='kv2')}}"
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
from ansible.module_utils.basic import AnsibleFallbackNotFound
from ansible.plugins.lookup import LookupBase

from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_read


class LookupModule(LookupBase):

    def _get_params(self, argspec, terms, kwargs):
        params = {}
        for arg in argspec:
            spec = argspec[arg]
            if arg in kwargs:
                params[arg] = kwargs[arg]
            elif 'default' in spec:
                params[arg] = spec.get('default')
            elif 'fallback' in spec:
                fall_func, fall_args = spec.get('fallback')
                try:
                    params[arg] = fall_func(*tuple(fall_args))
                except AnsibleFallbackNotFound:
                    pass

        params['secret'] = terms[0]
        try:
            params['key'] = terms[1]
        except IndexError:
            params['key'] = None
        return params

    def run(self, terms, variables=None, **kwargs):
        # self._display.v('Running lookup')
        argspec = hashivault_argspec()
        argspec['version'] = dict(required=False, type='int', default=1)
        argspec['mount_point'] = dict(required=False, type='str', default='secret')
        argspec['secret'] = dict(required=True, type='str')
        argspec['key'] = dict(required=False, type='str')
        argspec['default'] = dict(required=False, default=None, type='str')
        params = self._get_params(argspec, terms, kwargs)
        # self._display.v('ARGSPEC: ' + str(argspec))
        # self._display.v('KWARGS: ' + str(kwargs))
        # self._display.v('PARAMS: ' + str(params))
        result = hashivault_read(params=params)
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
