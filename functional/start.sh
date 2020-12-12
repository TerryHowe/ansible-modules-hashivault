#!/bin/bash -ex
#
# Start the test vault container
#
set -e
DOCKER_NAME=testvault
DOCKER_AGENT_NAME=testvaultagent
PORT=8201
AGENTPORT=8208
export VAULT_ADDR="http://127.0.0.1:${PORT}"

export AGENT_SOCK_DIR=$(mktemp -q -d /tmp/$0.agentsockdir.XXXXXX)
export VAULT_AGENT_ADDR_SOCK=${AGENT_SOCK_DIR}/agent.sock

TMP_CONFIG_DIR=$(mktemp -q -d /tmp/$0.XXXXXX)
TMP_CONFIG_VAULT="${TMP_CONFIG_DIR}/vault.json"
TMP_CONFIG_AGENT="${TMP_CONFIG_DIR}/agent.hcl"
trap "rm -rf $TMP_CONFIG_DIR" EXIT

cat <<EOF > $TMP_CONFIG_VAULT
{
	"backend": {
		"file": {
			"path": "/vault/file"
		}
	},
	"listener": {
		"tcp": {
			"address": "0.0.0.0:${PORT}",
			"tls_disable": 1
		}
	},
	"default_lease_ttl": "168h",
	"max_lease_ttl": "720h",
	"disable_mlock": true
}
EOF
chmod a+r $TMP_CONFIG_VAULT

docker stop $DOCKER_NAME 2>/dev/null || true
docker rm $DOCKER_NAME 2>/dev/null || true
docker run --name $DOCKER_NAME -h $DOCKER_NAME -d \
    --cap-add IPC_LOCK \
	-v $TMP_CONFIG_VAULT:/etc/vault/config.json:ro \
	--network host \
	vault server -config /etc/vault/config.json

#
# Wait for vault to come up
#
CNT=0
while ! curl -sI "$VAULT_ADDR/v1/sys/health" > /dev/null; do
	sleep 1
	CNT=$(expr $CNT + 1)
	if [ $CNT -gt 20 ]
	then
		docker logs $DOCKER_NAME
		exit 1
	fi
done


cat <<EOF > $TMP_CONFIG_AGENT
vault {
	address = "$VAULT_ADDR"
}
listener "tcp" {
	address = "0.0.0.0:$AGENTPORT"
	tls_disable = true
}
listener "unix" {
	address = "/agentsockdir/agent.sock"
	tls_disable = true
}
cache {}
EOF
chmod a+r $TMP_CONFIG_AGENT
chmod 0777 $AGENT_SOCK_DIR
touch $AGENT_SOCK_DIR/agent.sock

docker stop $DOCKER_AGENT_NAME 2>/dev/null || true
docker rm $DOCKER_AGENT_NAME 2>/dev/null || true
docker run --name $DOCKER_AGENT_NAME -h $DOCKER_AGENT_NAME -d \
    --cap-add IPC_LOCK \
	-v $AGENT_SOCK_DIR:/agentsockdir/:rw \
	-v $TMP_CONFIG_AGENT:/etc/vault/agent.hcl:ro \
	--network host \
	vault agent -config /etc/vault/agent.hcl

#
# Wait for vault agent to come up
#
CNT=0
while ! curl -sI "http://127.0.0.1:$AGENTPORT/v1/sys/health" > /dev/null; do
	sleep 1
	CNT=$(expr $CNT + 1)
	if [ $CNT -gt 20 ]
	then
		docker logs $DOCKER_AGENT_NAME
		exit 1
	fi
done

# Make the socket world accessible.
docker exec $DOCKER_AGENT_NAME chmod -R 'ugo+rwX' /agentsockdir

#
# Initialize the vault
#
ansible-playbook -v test_init.yml
source ./vaultenv.sh
ansible-playbook -v test_enable_kv.yml
exit $?
