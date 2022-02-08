Ansible Modules Hashivault
==========================

Ansible modules for Hashicorp Vault.

.. image:: https://img.shields.io/pypi/v/ansible-modules-hashivault.svg
   :alt: Latest version
   :target: https://pypi.python.org/pypi/ansible-modules-hashivault/
.. image:: https://pepy.tech/badge/ansible-modules-hashivault/month
   :alt: Downloads
   :target: https://pepy.tech/project/ansible-modules-hashivault
.. image:: https://github.com/TerryHowe/ansible-modules-hashivault/actions/workflows/test.yml/badge.svg?branch=main
   :alt: CI
   :target: https://github.com/TerryHowe/ansible-modules-hashivault/actions/workflows/test.yml
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :alt: License: MIT
   :target: https://opensource.org/licenses/MIT

Install this Ansible module:

* via ``pip``:

::

  pip install ansible-modules-hashivault

* via ``ansible-galaxy`` (requires ``hvac>=0.7.2``):

::

  ansible-galaxy install 'git+https://github.com/TerryHowe/ansible-modules-hashivault.git'

..

  Note: The ``hashicorp`` lookup plugin does not work with this last install method (`ansible/ansible#28770 <https://github.com/ansible/ansible/issues/28770>`_).
  You can fallback to the build-in lookup plugin: `hashi_vault <https://docs.ansible.com/ansible/latest/plugins/lookup/hashi_vault.html>`_

In most cases the Hashicorp Vault modules should be run on localhost.

Environmental Variables
-----------------------

The following variables need to be exported to the environment where you run ansible
in order to authenticate to your HashiCorp Vault instance:

  * `VAULT_ADDR`: url for vault
  * `VAULT_SKIP_VERIFY=true`: if set, do not verify presented TLS certificate before communicating with Vault server. Setting this variable is not recommended except during testing
  * `VAULT_AUTHTYPE`: authentication type to use: `token`, `userpass`, `github`, `ldap`, `approle`
  * `VAULT_LOGIN_MOUNT_POINT`: mount point for login defaults to auth type
  * `VAULT_TOKEN`: token for vault
  * `VAULT_ROLE_ID`: (required by `approle`)
  * `VAULT_SECRET_ID`: (required by `approle`)
  * `VAULT_USER`: username to login to vault
  * `VAULT_PASSWORD`: password to login to vault
  * `VAULT_CLIENT_KEY`: path to an unencrypted PEM-encoded private key matching the client certificate
  * `VAULT_CLIENT_CERT`: path to a PEM-encoded client certificate for TLS authentication to the Vault server
  * `VAULT_CACERT`: path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate
  * `VAULT_CAPATH`: path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate
  * `VAULT_AWS_HEADER`: X-Vault-AWS-IAM-Server-ID Header value to prevent replay attacks
  * `VAULT_NAMESPACE`: specify the Vault Namespace, if you have one

Documentation
-------------

There are a few simple examples in this document, but the full documentation can be found at:

https://terryhowe.github.io/ansible-modules-hashivault/modules/list_of_hashivault_modules.html


Reading and Writing
-------------------

The following example writes the giant secret with two values and then
reads the fie value. The `hashivault_secret` module is kv2 by default::

    ---
    - hosts: localhost
      tasks:
        - hashivault_secret:
            secret: giant
            data:
                foo: foe
                fie: fum
        - hashivault_read:
            secret: giant
            key: fie
            version: 2
          register: vault_read

The lookup plugin::

        - set_fact:
            looky: "{{lookup('hashivault', 'giant', 'foo', version=2)}}"

The hashivault_write, hashivault_read and the lookup plugin assume the
/secret mount point.  If you are accessing another mount point, use `mount_point`::

    ---
    - hosts: localhost
      tasks:
        - hashivault_secret_engine:
            name: stories
            backend: generic
        - hashivault_write:
            mount_point: /stories
            secret: stuart
            data:
                last: 'little'
        - hashivault_read:
            mount_point: /stories
            secret: stuart
            key: last
        - set_fact:
            book: "{{lookup('hashivault', 'stuart', 'last', mount_point='/stories')}}"

Version 2 of KV secret engine is also supported, just add `version: 2`::

    ---
        - hashivault_read:
            mount_point: /stories
            version: 2
            secret: stuart
            key: last
        - set_fact:
            book: "{{lookup('hashivault', 'stuart', 'last', mount_point='/stories', version=2)}}"


Initialization, Seal, and Unseal
--------------------------------

The real strength of this module is all the administrative functions you can do. See the documentation
mentioned above for more, but here is a small sample.

You may init the vault::

    ---
    - hosts: localhost
      tasks:
        - hashivault_init:
          register: vault_init

You may also seal and unseal the vault::

    ---
    - hosts: localhost
      vars:
        vault_keys:  "{{ lookup('env','VAULT_KEYS') }}"
      tasks:
        - hashivault_status:
          register: vault_status
        - block:
            - hashivault_seal:
              register: vault_seal
          when: "{{vault_status.status.sealed}} == False"
        - hashivault_unseal:
            keys: '{{vault_keys}}'

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
