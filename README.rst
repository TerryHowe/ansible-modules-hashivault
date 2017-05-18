Ansible Modules Hashivault
==========================

Ansible modules for Hashicorp Vault.

.. image:: https://img.shields.io/pypi/v/ansible-modules-hashivault.svg
   :alt: Latest version
   :target: https://pypi.python.org/pypi/ansible-modules-hashivault/
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :alt: License: MIT
   :target: https://opensource.org/licenses/MIT

Usage
-----

The following example writes the giant secret with two values and then
reads the fie value::

    ---
    - hosts: localhost
      vars:
        foo_value: 'fum'
        fie_value: 'fum'
      tasks:
        - hashivault_status:
          register: 'vault_status'
        - hashivault_write:
            secret: 'giant'
            data:
                foo: '{{foo_value}}'
                fie: '{{fie_value}}'
          register: 'vault_write'
        - hashivault_read:
            secret: 'giant'
            key: 'fie'
          register: 'vault_read'

The lookup plugin::

    looky: "{{lookup('hashivault', 'giant', 'foo')}}"

By default, the hashivault_write, hashivault_read and the lookup plugin assume the /secret mount point.  If you are accessing another mount point, start the secret with a '/'::

    ---
    - hosts: localhost
      tasks:
        - hashivault_write:
            secret: '/stories/stuart'
            data:
                last: 'little'
        - hashivault_read:
            secret: '/stories/charlotte'
            key: 'web'
        - set_fact:
            book: "{{lookup('hashivault', '/stories/charlotte', 'web')}}"

Get a list of secrets::

    ---
    - hosts: localhost
      tasks:
        - hashivault_list:
            secret: '/stories'
          register: vault

You may init the vault::

    ---
    - hosts: localhost
      tasks:
        - hashivault_init:
          register: 'vault_init'

You may also seal and unseal the vault::

    ---
    - hosts: localhost
      vars:
        vault_keys:  "{{ lookup('env','VAULT_KEYS') }}"
      tasks:
        - hashivault_status:
          register: 'vault_status'
        - block:
            - hashivault_seal:
              register: 'vault_seal'
          when: "{{vault_status.status.sealed}} == False"
        - hashivault_unseal:
            keys: '{{vault_keys}}'

Policy support::

    ---
    - hosts: localhost
      vars:
        name: 'terry'
        rules: >
            path "secret/{{name}}/*" {
              capabilities = ["create", "read", "update", "delete", "list"]
            } 
            path "secret/{{name}}" {
              capabilities = ["list"]
            } 
      tasks:
        - hashivault_policy_set:
            name: "{{name}}"
            rules: "{{rules}}"
          register: 'vault_policy_set'
        - hashivault_policy_get:
            name: '{{name}}'
          register: 'vault_policy_get'
        - hashivault_policy_list:
          register: 'vault_policy_list'

Add and delete users for userpass::

    ---
    - hosts: localhost
      vars:
        username: 'portugal'
        userpass: 'Th3m@n!!'
      tasks:
        - hashivault_userpass_create:
            name: "{{username}}"
            pass: "{{userpass}}"
            policies: "{{username}}"
          register: 'vault_userpass_create'
    
        - hashivault_userpass_delete:
            name: "{{username}}"
          register: 'vault_userpass_delete'

Handle auth backends::

    ---
    - hosts: localhost
      tasks:
        - hashivault_auth_list:
          register: 'vault_auth_list'
        - block:
          - hashivault_auth_enable:
              name: "userpass"
            register: 'vault_auth_enable'
          when: "'userpass/' not in vault_auth_list.backends"

Handle audit backends::

    ---
    - hosts: localhost
      tasks:
        - hashivault_audit_list:
          register: 'vault_audit_list'
        - block:
          - hashivault_audit_enable:
              name: "syslog"
            register: 'vault_audit_enable'
          when: "'syslog/' not in vault_audit_list.backends"

If you are not using the VAULT_ADDR and VAULT_TOKEN environment variables,
you may be able to simplify your playbooks with an action plugin.  This can
be some somewhat similar to this `example action plugin <https://terryhowe.wordpress.com/2016/05/02/setting-ansible-module-defaults-using-action-plugins/>`_.

License
-------

[MIT](https://github.com/TerryHowe/ansible-modules-hashivault/blob/master/LICENSE)
