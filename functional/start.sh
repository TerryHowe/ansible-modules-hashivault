#!/bin/bash -ex
#
# Start the test vault container
#
set -e
DOCKER_NAME=testvault
PORT=8201
export VAULT_ADDR="http://127.0.0.1:${PORT}"

TMP_CONFIG=$(mktemp -q /tmp/$0.XXXXXX)
trap "rm $TMP_CONFIG" EXIT

cat <<EOF > $TMP_CONFIG
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
chmod a+r $TMP_CONFIG

docker stop $DOCKER_NAME 2>/dev/null || true
docker rm $DOCKER_NAME 2>/dev/null || true
docker run --name $DOCKER_NAME -h $DOCKER_NAME -d \
    --cap-add IPC_LOCK \
	-p 127.0.0.1:${PORT}:${PORT} \
	-v $TMP_CONFIG:/etc/vault/config.hcl:ro \
	vault server -config /etc/vault/config.hcl

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
