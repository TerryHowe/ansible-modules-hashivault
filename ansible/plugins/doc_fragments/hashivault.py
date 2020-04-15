class ModuleDocFragment(object):
    # Standard documentation
    DOCUMENTATION = r'''
    author: "Terry Howe (@TerryHowe)"
    requirements:
        - hvac>=0.10.1
        - ansible>=2.0.0
        - requests
    options:
        url:
            description:
                - url for vault
            default: to environment variable C(VAULT_ADDR)
        ca_cert:
            description:
                - "path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate"
            default: to environment variable C(VAULT_CACERT)
        ca_path:
            description:
                - "path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate : if ca_cert is specified, its value will take precedence"
            default: to environment variable C(VAULT_CAPATH)
        client_cert:
            description:
                - "path to a PEM-encoded client certificate for TLS authentication to the Vault server"
            default: to environment variable C(VAULT_CLIENT_CERT)
        client_key:
            description:
                - "path to an unencrypted PEM-encoded private key matching the client certificate"
            default: to environment variable C(VAULT_CLIENT_KEY)
        verify:
            description:
                - "if set, do not verify presented TLS certificate before communicating with Vault server : setting this variable is not recommended except during testing"
            default: to environment variable C(VAULT_SKIP_VERIFY)
        authtype:
            description:
                - authentication type
            default: token
            choices: ["token", "userpass", "github", "ldap", "approle"]
        token:
            description:
                - token for vault
            default: to environment variable C(VAULT_TOKEN)
        username:
            description:
                - username to login to vault.
            default: to environment variable C(VAULT_USER)
        password:
            description:
                - password to login to vault.
            default: to environment variable C(VAULT_PASSWORD)
'''