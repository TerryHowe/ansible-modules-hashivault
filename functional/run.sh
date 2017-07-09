#!/bin/bash -ex
#
# This test runs a vault container on the host network port 8201.
#
./start.sh

source ./vaultenv.sh
ansible-playbook -v test.yml
ansible-playbook -v test_auth.yml
ansible-playbook -v test_policy.yml
ansible-playbook -v test_status.yml
ansible-playbook -v test_userpass.yml
ansible-playbook -v test_secret.yml
ansible-playbook -v test_complex.yml
ansible-playbook -v test_unseal.yml

./stop.sh
