#
# Run uninitialized docker vault
#
docker run --cap-add=IPC_LOCK -e 'VAULT_LOCAL_CONFIG={"backend": {"file": {"path": "/vault/file"}}, "listener": {"tcp": {"address": "0.0.0.0:8200", "tls_disable": 1}}, "default_lease_ttl": "168h", "max_lease_ttl": "720h"}' vault server
