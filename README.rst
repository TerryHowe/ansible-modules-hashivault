Ansible Modules Hashivault
==========================

Ansible modules for Hashicorp Vault.

.. image:: https://img.shields.io/pypi/v/ansible-modules-hashivault.svg
   :alt: Latest version
   :target: https://pypi.python.org/pypi/ansible-modules-hashivault/

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

You may also, seal and unseal the vault::

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

If you are not using the VAULT_ADDR and VAULT_TOKEN environment variables,
you may be able to simplify your playbooks with an action plugin.  This can
be some somewhat similar to this `example action plugin <https://terryhowe.wordpress.com/2016/05/02/setting-ansible-module-defaults-using-action-plugins/>`_.

License
-------

MIT
