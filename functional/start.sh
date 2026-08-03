#!/bin/bash -ex
#
# Start the test vault container
#
set -e
DOCKER_NAME=testvault
PORT=8201
export VAULT_ADDR="http://127.0.0.1:${PORT}"

# Pass the config through VAULT_LOCAL_CONFIG rather than bind-mounting a file.
# Docker Desktop on macOS does not share /tmp, so a single-file bind mount from
# there silently becomes an empty directory inside the container and vault fails
# with "A storage backend must be specified".
VAULT_LOCAL_CONFIG=$(cat <<EOF
storage "file" {
  path = "/vault/file"
}

"listener" "tcp" {
  "address" = "0.0.0.0:${PORT}"

  "tls_disable" = 1
}

"default_lease_ttl" = "168h"

"max_lease_ttl" = "720h"

"disable_mlock" = true
EOF
)
export VAULT_LOCAL_CONFIG

# Current is not tagged latest and vault won't push images
# after 1.14, but this image is okay today
# # Current is not tagged latest and vault won't push images
# after 1.14, but this image is okay today
TAG=latest
TAG=1.18
docker stop $DOCKER_NAME 2>/dev/null || true
docker rm -f $DOCKER_NAME 2>/dev/null || true
docker run --name $DOCKER_NAME -h $DOCKER_NAME -d \
    --cap-add IPC_LOCK \
	-p 127.0.0.1:${PORT}:${PORT} \
	-e VAULT_LOCAL_CONFIG \
	hashicorp/vault:${TAG} server

#
# Wait for vault to come up
#
CNT=0
while ! curl -sI "$VAULT_ADDR/v1/sys/health" > /dev/null; do
	sleep 0.1
	CNT=$(expr $CNT + 1)
	if [ $CNT -gt 20 ]
	then
		docker logs $DOCKER_NAME
		exit 1
	fi
done

#
# Initialize the vault
#
ansible-playbook -v test_init.yml
source ./vaultenv.sh
ansible-playbook -v test_enable_kv.yml
exit $?
