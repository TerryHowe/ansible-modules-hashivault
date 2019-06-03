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
ansible-playbook -v test_enable_kv.yml
# ansible-playbook -v test_mounts.yml enable after hvac 9.2 released
ansible-playbook -v test_write.yml
ansible-playbook -v test_check.yml --check
ansible-playbook -v test_read.yml
ansible-playbook -v test_full_path.yml
ansible-playbook -v test_create_ec2_role.yml
ansible-playbook -v test_list.yml
ansible-playbook -v test_lookup.yml
ansible-playbook -v test_delete.yml
ansible-playbook -v test_auth.yml
ansible-playbook -v test_auth_method.yml
ansible-playbook -v test_azure_auth_config.yml
# ansible-playbook -v test_azure_auth_role.yml wont work till hvac 9.2, issues/451 
ansible-playbook -v test_secret_list.yml
# ansible-playbook -v test_db_config.yml cannot run without true db connectivity
# ansible-playbook -v test_db_role.yml cannot run without true db connectivity
ansible-playbook -v test_azure_config.yml
# ansible-playbook -v test_azure_role.yml cannot run without true azure connectivity
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
ansible-playbook -v test_userpass_idempotent.yml
source ./userpassenv.sh
ansible-playbook -v --extra-vars='namespace=userpass/' test_write.yml test_read.yml test_lookup.yml
source ./vaultenv.sh

./stop.sh
