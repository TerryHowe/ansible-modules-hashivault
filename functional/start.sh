#!/bin/bash -ex
#
# Start the test vault container
#
export NAME=test_vault
export PORT=8201
export VAULT_ADDR="http://127.0.0.1:${PORT}"

docker stop $NAME 2>/dev/null || true
docker rm $NAME 2>/dev/null || true
docker run --name $NAME -h $NAME -d --cap-add=IPC_LOCK --network=host -e 'VAULT_LOCAL_CONFIG={"backend": {"file": {"path": "/vault/file"}}, "listener": {"tcp": {"address": "0.0.0.0:8201", "tls_disable": 1}}, "default_lease_ttl": "168h", "max_lease_ttl": "720h"}' vault server

#
# Initialize the vault
#
ansible-playbook -v test_init.yml
