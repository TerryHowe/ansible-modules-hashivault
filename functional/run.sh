#!/bin/bash -ex
ansible-playbook -v test_init.yml
ansible-playbook -v test.yml
ansible-playbook -v test_auth.yml
ansible-playbook -v test_policy.yml
ansible-playbook -v test_status.yml
ansible-playbook -v test_userpass.yml
ansible-playbook -v test_secret.yml
# do last
ansible-playbook -v test_unseal.yml
