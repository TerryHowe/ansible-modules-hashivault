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
        vault_keys:  "{{ lookup('env','VAULT_KEYS').split(' ')[0:3] }}"
      tasks:
        - hashivault_status:
          register: 'vault_status'
        - block:
            - hashivault_seal:
              register: 'vault_seal'
            - assert: { that: "{{vault_seal.changed}} == True" }
            - assert: { that: "{{vault_seal.rc}} == 0" }
          when: "{{vault_status.status.sealed}} == False"
        - hashivault_unseal:
            key: '{{item}}'
          register: 'vault_unseal'
          with_items: "{{vault_keys}}"

If you are not using the VAULT_ADDR and VAULT_TOKEN environment variables,
you may be able to simplify your playbooks with an action plugin.  This can
be some somewhat similar to this `example action plugin <https://terryhowe.wordpress.com/2016/05/02/setting-ansible-module-defaults-using-action-plugins/>`_.

License
-------

MIT
