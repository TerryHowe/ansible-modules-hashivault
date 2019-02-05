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

Install this Ansible module:

* via ``pip``:

::

  pip install ansible-modules-hashivault

* via ``ansible-galaxy`` (requires ``hvac>=0.7.0``):

::

  ansible-galaxy install 'git+https://github.com/TerryHowe/ansible-modules-hashivault.git'

..

  Note: The ``hashicorp`` lookup plugin does not work with this last install method (`ansible/ansible#28770 <https://github.com/ansible/ansible/issues/28770>`_).
  You can fallback to the build-in lookup plugin: `hashi_vault <https://docs.ansible.com/ansible/latest/plugins/lookup/hashi_vault.html>`_

In most cases the Hashicorp Vault modules should be run on localhost.

Environmental Variables
-------------------

The following variables need to be exported to the environment where you run ansible
in order to authenticate to your HashiCorp Vault instance:

  * `VAULT_ADDR`: url for vault
  * `VAULT_SKIP_VERIFY=true`: if set, do not verify presented TLS certificate before communicating with Vault server. Setting this variable is not recommended except during testing
  * `VAULT_AUTHTYPE`: authentication type to use: `token`, `userpass`, `github`, `ldap`, `approle`
  * `VAULT_TOKEN`: token for vault
  * `VAULT_ROLE_ID`: (required by `approle`)
  * `VAULT_SECRET_ID`: (required by `approle`)
  * `VAULT_USER`: username to login to vault
  * `VAULT_PASSWORD`: password to login to vault
  * `VAULT_CLIENT_KEY`: path to an unencrypted PEM-encoded private key matching the client certificate
  * `VAULT_CLIENT_CERT`: path to a PEM-encoded client certificate for TLS authentication to the Vault server
  * `VAULT_CACERT`: path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate
  * `VAULT_CAPATH`: path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate
  * `VAULT_NAMESPACE`: specify the Vault Namespace, if you have one

Generated Documentation
-----------------------

https://terryhowe.github.io/ansible-modules-hashivault/modules/list_of_hashivault_modules.html


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

Ansible does not handle binary data well, so these modules are provided for convenience to read/write files::

    ---
    - hashivault_read_to_file:
        secret: 'ssl_certs'
        key: 'der_format'
        dest: 'ssl_cert.cer'
    - hashivault_write_from_file:
        secret: 'ssl_certs'
        key: 'der_format'
        path: 'ssl_cert.cer'

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

Policy From A file
------------------

Policy from a file support::

    ---
    - hosts: localhost
      vars:
        name: 'drew'

      tasks:
        - hashivault_policy_set_from_file:
            name: "{{name}}"
            rules_file: /home/drew/my_policy.hcl
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

Tune auth backends::

    ---
    - hosts: localhost
      tasks:
        - name: Tune ephermal secret store
          hashivault_mount_tune:
            mount_point: ephemeral
            default_lease_ttl: 3600
            max_lease_ttl: 8600

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
    - hashivault_token_revoke:
        revoke_token: "{{client_token}}"
      register: "vault_token_revoke"
    - hashivault_token_renew:
        renew_token: "{{client_token}}"
      register: "vault_token_renew"

Approle
-------

Approle modules::

    ---
    - hashivault_approle_role_create:
        name: testrole
        policies:
          - approle_test_policy
    - hashivault_approle_role_id:
        name: testrole
      register: 'vault_role_id'
    - hashivault_approle_role_secret_create:
        name: testrole
      register: 'vault_role_secret_create'

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
