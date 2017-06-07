#!/bin/bash -ex
#
# Make sure you have a minimal set of environment variables set.  For example:
#VAULT_ADDR=http://172.17.0.2:8200
#VAULT_TOKEN=da20ff3b-3b56-82f9-19bb-56be55b77c92
#VAULT_KEYS=DsGodBlDavvj4GSKO7HlD5RqVYuywBFWdGGziAOyPi8=
#
# For now run the init test manually since this currently does
# not capture the keys for later use
#
#ansible-playbook -v test_init.yml
ansible-playbook -v test.yml
ansible-playbook -v test_auth.yml
ansible-playbook -v test_policy.yml
ansible-playbook -v test_status.yml
ansible-playbook -v test_userpass.yml
ansible-playbook -v test_secret.yml
ansible-playbook -v test_complex.yml
# do last
ansible-playbook -v test_unseal.yml
