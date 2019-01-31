#!/bin/bash -ex
#
# This test runs a vault container on the host network port 8201.
#
cd "$(dirname "$0")"
HOMEDIR=$(dirname $(dirname $PWD))
HOME=${HOME:-${HOMEDIR}}
export HOME
./start.sh

source ./vaultenv.sh
ansible-playbook -v test_check.yml --check
ansible-playbook -v test_write.yml
ansible-playbook -v test_read.yml
ansible-playbook -v test_full_path.yml
ansible-playbook -v test_create_ec2_role.yml
ansible-playbook -v test_list.yml
ansible-playbook -v test_lookup.yml
ansible-playbook -v test_delete.yml
ansible-playbook -v test_auth.yml
ansible-playbook -v test_secret_list.yml
ansible-playbook -v test_policy.yml
ansible-playbook -v test_status.yml
ansible-playbook -v test_not_there.yml
ansible-playbook -v test_ephemeral.yml
ansible-playbook -v test_generate_root.yml
# ansible-playbook -v test_kv2.yml fais because hvac issue #385
ansible-playbook -v test_tokens.yml
ansible-playbook -v test_audit.yml
ansible-playbook -v test_read_write_file.yml
ansible-playbook -v test_environment_lookup.yml
ansible-playbook -v test_unseal.yml
ansible-playbook -v test_rekey.yml
# test_rekey.yml changes unseal keys, need to update VAULT_KEYS
# for further test, if any.
source ./vaultenv.sh

# approle
ansible-playbook -v test_approle.yml
source ./approlenv.sh
ansible-playbook -v --extra-vars='namespace=application/' test_write.yml test_read.yml test_lookup.yml
source ./vaultenv.sh

# userpass
ansible-playbook -v test_userpass.yml
source ./userpassenv.sh
ansible-playbook -v --extra-vars='namespace=userpass/' test_write.yml test_read.yml test_lookup.yml
source ./vaultenv.sh

./stop.sh
