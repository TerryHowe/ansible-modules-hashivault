Ansible Modules Hashivault
==========================

Ansible modules for Hashicorp Vault.

.. image:: https://img.shields.io/pypi/v/ansible-modules-hashivault.svg
   :alt: Latest version
   :target: https://pypi.python.org/pypi/ansible-modules-hashivault/

Usage
-----

The following example simply connects to Quay and lists the organization in
the repository.::

    ---
    - hosts: localhost
      tasks:
        - hashivault_write:
            secret: giant
            data:
                foo: foe
                fie: fum
        - hashivault_read: secret='giant' key='fie' register='fie'
        - debug: msg="Value is {{fie.value}}"

If you are not using the VAULT_ADDR and VAULT_TOKEN environment variables,
you may be able to simplify your playbooks with an action plugin.  This can
be some somewhat similar to this `example action plugin <https://terryhowe.wordpress.com/2016/05/02/setting-ansible-module-defaults-using-action-plugins/>`_.

License
-------

MIT
