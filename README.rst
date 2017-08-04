Ansible Modules Hashivault
==========================

Ansible modules for Hashicorp Vault.

.. image:: https://img.shields.io/pypi/v/ansible-modules-hashivault.svg
   :alt: Latest version
   :target: https://pypi.python.org/pypi/ansible-modules-hashivault/
.. image:: https://travis-ci.org/TerryHowe/ansible-modules-hashivault.svg?branch=master
   :alt: Travis CI
   :target: https://travis-ci.org/TerryHowe/ansible-modules-hashivault
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :alt: License: MIT
   :target: https://opensource.org/licenses/MIT

In most cases the Hashicorp Vault modules should be run on localhost.

Reading and Writing
-------------------

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

Initialization, Seal, and Unseal
--------------------------------

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

Policy
------

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

User Management
---------------

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

Authentication Backends
-----------------------

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

Audit Backends
--------------

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

Rekey Vault
-----------

Various rekey vault operations::

    ---
    - hashivault_rekey_init:
        secret_shares: 7
        secret_threshold: 4
    - hashivault_rekey:
      key: '{{vault_key}}'
      nonce: '{{nonce}}'
    - hashivault_rekey_status:
      register: "vault_rekey_status"
    - hashivault_rekey_cancel:
      register: "vault_rekey_cancel"

Secret Backends
---------------

Enable and disable various secret backends::

    ---
    - hashivault_secret_list:
      register: 'hashivault_secret_list'
    - hashivault_secret_enable:
        name: "ephemeral"
        backend: "generic"
    - hashivault_secret_disable:
        name: "ephemeral"
        backend: "generic"

Token Manipulation
------------------

Various token manipulation modules::

    ---
    - hashivault_token_create:
        display_name: "syadm"
        policies: ["sysadm"]
        renewable: True
        token: "{{vault_root_token}}"
      register: "vault_token_admin"
    - hashivault_token_lookup:
        lookup_token: "{{client_token}}"
      register: "vault_token_lookup"

Action Plugin
-------------

If you are not using the VAULT_ADDR and VAULT_TOKEN environment variables,
you may be able to simplify your playbooks with an action plugin.  This can
be some somewhat similar to this `example action plugin <https://terryhowe.wordpress.com/2016/05/02/setting-ansible-module-defaults-using-action-plugins/>`_.

Developer Note
--------------
One of the complicated problems with development and testing of this module is
:code:`ansible/module_utils/hashivault.py` is not a directory in itself which
in my opinion is a problem with ansible.  Because of this limitation with
ansible, :code:`pip install -e .` does not work like it would for other
projects.  Two potential ways to work around this issue are either use the
:code:`link.sh` script in the top level directory or run for every change::

    rm -rf dist; python setup.py sdist
    pip install ./dist/ansible-modules-hashivault-*.tar.gz

License
-------

`MIT <https://github.com/TerryHowe/ansible-modules-hashivault/blob/master/LICENSE>`_.
