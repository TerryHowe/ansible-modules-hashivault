#!/usr/bin/env python
from distutils.core import setup

files = [
    "ansible/module_utils",
    "ansible/modules/hashivault",
]

setup(name='ansible-modules-hashivault',
      version='0.8',
      description='Ansible Modules for Hashicorp Vault',
      author='Terry Howe',
      author_email='terrylhowe@example.com',
      url='https://github.com/TerryHowe/ansible-modules-hashivault',
      packages=files,
)
