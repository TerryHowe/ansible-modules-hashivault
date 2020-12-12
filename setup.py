#!/usr/bin/env python
from setuptools import setup

py_files = [
    "plugins/module_utils/hashivault",
    "plugins/lookup/hashivault",
    "plugins/action/hashivault_read_to_file",
    "plugins/action/hashivault_write_from_file",
    "plugins/doc_fragments/hashivault",
]
files = [
    "plugins/modules",
]

long_description = open('README.rst', 'r').read()

setup(
    name='ansible-modules-hashivault',
    version='4.6.2',
    description='Ansible Modules for Hashicorp Vault',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Terry Howe',
    author_email='terrylhowe@example.com',
    url='https://github.com/TerryHowe/ansible-modules-hashivault',
    py_modules=py_files,
    packages=files,
    install_requires=[
        'ansible>=2.9.0',
        'hvac>=0.9.5',
        'requests',
    ],
)
