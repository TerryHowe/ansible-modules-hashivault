#!/usr/bin/env python
from distutils.core import setup

files = [
    "ansible/module_utils",
    "ansible/modules/hashivault",
]

long_description = """

Ansible modules for Hashicorp Vault.

Usage
-----

The following example writes the giant secret with two values and then
reads the fie value::

    ---
    - hosts: localhost
      tasks:
        - hashivault_write:
            secret: giant
            data:
                foo: foe
                fie: fum
        - hashivault_read:
            secret: 'giant'
            key: 'fie'
          register: 'fie'
        - debug: msg="Value is {{fie.value}}"

If you are not using the VAULT_ADDR and VAULT_TOKEN environment variables,
you may be able to simplify your playbooks with an action plugin.  This can
be some somewhat similar to this `example action plugin <https://terryhowe.wordpress.com/2016/05/02/setting-ansible-module-defaults-using-action-plugins/>`_.

"""

setup(name='ansible-modules-hashivault',
    version='2.5.0',
    description='Ansible Modules for Hashicorp Vault',
    long_description=long_description,
    author='Terry Howe',
    author_email='terrylhowe@example.com',
    url='https://github.com/TerryHowe/ansible-modules-hashivault',
    packages=files,
    install_requires = [
        'hvac',
        'ansible>2.0.0',
    ],
)
