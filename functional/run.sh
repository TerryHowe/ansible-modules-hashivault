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
ansible-playbook -v test_mounts.yml
ansible-playbook -v test_write.yml
ansible-playbook -v test_secret.yml
ansible-playbook -v test_check.yml --check
ansible-playbook -v test_read.yml
ansible-playbook -v test_full_path.yml
ansible-playbook -v test_aws_auth_config.yml
ansible-playbook -v test_aws_auth_role.yml
ansible-playbook -v test_list.yml
ansible-playbook -v test_lookup.yml
ansible-playbook -v test_delete.yml
ansible-playbook -v test_delete_permanent.yml
ansible-playbook -v test_auth.yml
ansible-playbook -v test_auth_method.yml
ansible-playbook -v test_azure_auth_config.yml
ansible-playbook -v test_azure_auth_role.yml
ansible-playbook -v test_k8_auth.yml
ansible-playbook -v test_oidc_auth_method_config.yml
ansible-playbook -v test_oidc_auth_role.yml
ansible-playbook -v test_secret_engine.yml
ansible-playbook -v test_secret_list.yml
# ansible-playbook -v test_namespace.yml cannot run without enterprise
# ansible-playbook -v test_db_config.yml cannot run without true db connectivity
# ansible-playbook -v test_db_role.yml cannot run without true db connectivity
ansible-playbook -v test_consul_config.yml
ansible-playbook -vvv test_consul_role.yml
# ansible-playbook -v test_azure_config.yml
# ansible-playbook -v test_azure_role.yml cannot run without true azure connectivity
ansible-playbook -v test_policy.yml
ansible-playbook -v test_policy_old.yml
ansible-playbook -v test_status.yml
ansible-playbook -v test_not_there.yml
ansible-playbook -v test_ephemeral.yml
ansible-playbook -v test_generate_root.yml
ansible-playbook -v test_kv2.yml
ansible-playbook -v test_cas.yml
ansible-playbook -v test_tokens.yml
ansible-playbook -v test_audit.yml
ansible-playbook -v test_audit_old.yml
ansible-playbook -v test_read_write_file.yml
ansible-playbook -v test_environment_lookup.yml
ansible-playbook -v test_unseal.yml
ansible-playbook -v test_identity_group.yml
ansible-playbook -v test_identity_entity.yml
ansible-playbook -v test_ldap_group.yml
ansible-playbook -v test_pki.yml
ansible-playbook -v test_rekey.yml
# test_rekey.yml changes unseal keys, need to update VAULT_KEYS
# for further test, if any.
source ./vaultenv.sh

ansible-playbook -v test_rekey_verify.yml
# test_rekey_verify.yml changes unseal keys, need to update VAULT_KEYS
# for further test, if any.
source ./vaultenv.sh

# approle
ansible-playbook -v test_approle.yml
ansible-playbook -v test_approle_check_mode.yml
source ./approlenv.sh
ansible-playbook -v --extra-vars='namespace=application/' test_write.yml test_read.yml test_lookup.yml
source ./vaultenv.sh
ansible-playbook -v test_approle_mount_point.yml
source ./approlenv.sh
ansible-playbook -v --extra-vars='namespace=lightning/' test_write.yml test_read.yml test_lookup.yml
source ./vaultenv.sh
ansible-playbook -v test_approle_old.yml

# tokenrole
ansible-playbook -v test_token_role.yml
ansible-playbook -v test_token_role_check_mode.yml

# sshrole
ansible-playbook -v test_ssh_role.yml
ansible-playbook -v test_ssh_role_check_mode.yml

# userpass
ansible-playbook -v test_userpass.yml
ansible-playbook -v test_userpass_idempotent.yml
ansible-playbook -v test_userpass_no_pass.yml
ansible-playbook -v test_userpass_no_policy.yml
source ./userpassenv.sh
ansible-playbook -v --extra-vars='namespace=userpass/' test_write.yml test_read.yml test_lookup.yml
source ./vaultenv.sh

./stop.sh
