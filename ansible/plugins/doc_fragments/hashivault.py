class ModuleDocFragment(object):
    # Standard documentation
    DOCUMENTATION = r'''
    requirements:
        - hvac>=0.10.1
        - ansible>=2.0.0
        - requests
    options:
        url:
            description:
                - url for vault
            default: to environment variable `VAULT_ADDR`
        ca_cert:
            description:
                - Path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate
            default: to environment variable `VAULT_CACERT`
        ca_path:
            description:
                - Path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate. If
                  ca_cert is specified, its value will take precedence
            default: to environment variable `VAULT_CAPATH`
        client_cert:
            description:
                - Path to a PEM-encoded client certificate for TLS authentication to the Vault server
            default: to environment variable `VAULT_CLIENT_CERT`
        client_key:
            description:
                - Path to an unencrypted PEM-encoded private key matching the client certificate
            default: to environment variable `VAULT_CLIENT_KEY`
        verify:
            description:
                - If set, do not verify presented TLS certificate before communicating with Vault server. Setting this
                  variable is not recommended except during testing
            default: to environment variable `VAULT_SKIP_VERIFY`
        authtype:
            description:
                - authentication type
            default: token or environment variable `VAULT_AUTHTYPE`
            choices: ["token", "userpass", "github", "ldap", "approle"]
        login_mount_point:
            description:
                - authentication mount point
            default: value of authtype or environment varialbe `VAULT_LOGIN_MOUNT_POINT`
        token:
            description:
                - token for vault
            default: to environment variable `VAULT_TOKEN`
        username:
            description:
                - username to login to vault.
            default: to environment variable `VAULT_USER`
        password:
            description:
                - password to login to vault.
            default: to environment variable `VAULT_PASSWORD`
        aws_header:
            description:
                - X-Vault-AWS-IAM-Server-ID Header value to prevent replay attacks.
            default: to environment variable `VAULT_AWS_HEADER`
        namespace:
            description:
                - namespace for vault
            default: to environment variable VAULT_NAMESPACE
'''
