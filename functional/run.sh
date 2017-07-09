#!/bin/bash -ex
#
# This test runs a vault container on the host network port 8201.
#
NAME=test_vault
PORT=8201

docker stop $NAME 2>/dev/null || true
docker rm $NAME 2>/dev/null || true
docker run --name $NAME -h $NAME -d --cap-add=IPC_LOCK --network=host -e 'VAULT_LOCAL_CONFIG={"backend": {"file": {"path": "/vault/file"}}, "listener": {"tcp": {"address": "0.0.0.0:8201", "tls_disable": 1}}, "default_lease_ttl": "168h", "max_lease_ttl": "720h"}' vault server

export VAULT_ADDR="http://127.0.0.1:${PORT}"
ansible-playbook -v test_init.yml
source ./vaultenv.sh
ansible-playbook -v test.yml
ansible-playbook -v test_auth.yml
ansible-playbook -v test_policy.yml
ansible-playbook -v test_status.yml
ansible-playbook -v test_userpass.yml
ansible-playbook -v test_secret.yml
ansible-playbook -v test_complex.yml
ansible-playbook -v test_unseal.yml
rm -f ./vaultenv.sh
docker stop $NAME || true
