Ansible Modules Hashivault
==========================

Ansible modules for Hashicorp Vault.

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

License
-------

MIT
