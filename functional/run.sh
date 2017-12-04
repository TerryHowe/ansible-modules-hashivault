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
ansible-playbook -v test_secrets_w_policy_tokens.yml
ansible-playbook -v test_audit.yml
ansible-playbook -v test_unseal.yml
ansible-playbook -v test_rekey.yml
# test_rekey.yml changes unseal keys, need to update VAULT_KEYS
# for further test, if any.
source ./vaultenv.sh

./stop.sh
