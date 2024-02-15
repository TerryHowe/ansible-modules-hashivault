#!/usr/bin/env python
from setuptools import setup

py_files = [
    "ansible/module_utils/hashivault",
    "ansible/plugins/lookup/hashivault",
    "ansible/plugins/action/hashivault_read_to_file",
    "ansible/plugins/action/hashivault_write_from_file",
    "ansible/plugins/doc_fragments/hashivault",
]
files = [
    "ansible/modules/hashivault",
]

long_description = open('README.rst', 'r').read()

setup(
    name='ansible-modules-hashivault',
    version='5.1.2',
    description='Ansible Modules for Hashicorp Vault',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Terry Howe',
    author_email='terrylhowe@example.com',
    url='https://github.com/TerryHowe/ansible-modules-hashivault',
    py_modules=py_files,
    packages=files,
    install_requires=[
        'ansible-core>=2.12.0',
        'hvac>=1.2.1',
        'requests',
    ],
)
