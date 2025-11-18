# AGENTS.md

This file provides guidance for AI coding agents working on the ansible-modules-hashivault project.

## Project Overview

This project provides Ansible modules for interacting with HashiCorp Vault. It includes over 90 modules covering all major Vault operations including:

- Secret management (read, write, list, delete)
- Authentication methods (token, userpass, LDAP, approle, AWS, Azure, K8s, JWT/OIDC)
- Secret engines (KV, PKI, Database, Consul, SSH, Azure)
- Administrative operations (init, seal/unseal, rekey, generate root)
- Policy and ACL management
- Identity management (entities, groups, aliases)
- Audit backend configuration

The modules are designed to run on localhost and communicate with a remote Vault server.

## Code Structure

- `ansible/modules/hashivault/` - All Ansible modules (90+ modules)
- `ansible/module_utils/hashivault.py` - Shared utility functions and client initialization
- `ansible/plugins/lookup/` - Lookup plugins for Vault integration
- `ansible/plugins/action/` - Action plugins for file operations
- `functional/` - Functional test suite
- `example/` - Example playbooks

## Build and Test

### Running Tests

Tests are orchestrated via tox:

```bash
# Run all tests (lint + functional tests + docs)
tox

# Run only linting
tox -e pep8

# Run only functional tests
tox -e py39

# Run only documentation generation
tox -e docs
```

Functional tests require a running Vault instance and are executed via:

```bash
bash -ex functional/run.sh
```

### Building Documentation

```bash
./makedocs.sh
```

Documentation is generated from module docstrings and published to GitHub Pages.

## Code Style and Conventions

### Python Style

- **PEP8 compliant** with max line length of **120 characters**
- **Indentation**: 4 spaces (no tabs)
- Linting via `pycodestyle --max-line-length=120 ansible`
- Always add a final newline to files
- Use UTF-8 encoding
- Trim trailing whitespace

### YAML Style

- **Indentation**: 2 spaces
- Use lowercase `true`/`false` for booleans

### Module Structure

All modules should follow this pattern:

1. Import required libraries (hvac, ansible.module_utils)
2. Define ANSIBLE_METADATA with status and supported_by
3. Define DOCUMENTATION string with module description, options, and examples
4. Define RETURN string documenting return values
5. Implement main logic using hashivault utilities
6. Use `hashivault_argspec()` for common Vault connection parameters
7. Use `hashivault_init()` to create the AnsibleModule instance
8. Use `hashivault_client()` to create the Vault client

### Security Considerations

**CRITICAL**: Never log sensitive data

- Always mark sensitive parameters with `no_log=True` (tokens, passwords, role_ids, secret_ids)
- The shared module utils automatically excludes common false positives (0, 1, True, False, 'ttl') from no_log
- Use `module.no_log_values.discard()` for legitimate non-sensitive values that trigger false positives

**Vault Authentication**: Modules support multiple auth types via environment variables:
- VAULT_ADDR, VAULT_TOKEN, VAULT_AUTHTYPE, VAULT_USER, VAULT_PASSWORD
- VAULT_ROLE_ID, VAULT_SECRET_ID (for approle)
- VAULT_CACERT, VAULT_CLIENT_CERT, VAULT_CLIENT_KEY (for TLS)
- VAULT_NAMESPACE (for Enterprise namespaces)

## Testing Guidelines

- Each module should have corresponding functional tests in `functional/`
- Tests use a local Vault container for integration testing
- Test files are named `test_hashivault_<module_name>.sh`
- All tests must pass before merging
- Support for `check_mode` should be added where applicable

## Commit Message Format

Use conventional commit format:

- `fix:` - Bug fixes
- `feat:` - New features or modules
- `chore:` - Maintenance tasks, dependency updates
- `docs:` - Documentation updates
- `test:` - Test additions or fixes

Examples:
```
fix: audit test broken with vault change
feat: add disable_local_ca_jwt param in k8s auth config
chore: update readme
```

All commits are GPG-signed by maintainers.

## Pull Request Guidelines

- Ensure all CI checks pass (lint, tests, docs)
- Update documentation if adding new modules or parameters
- Add functional tests for new functionality
- Follow existing code patterns and conventions
- PRs are merged to `main` branch

## Development Setup

Standard pip installation doesn't work due to Ansible's module structure limitations. Use one of:

```bash
# Option 1: Use the link script
./link.sh

# Option 2: Build and install from dist
rm -rf dist
python setup.py sdist
pip install ./dist/ansible-modules-hashivault-*.tar.gz
```

## Dependencies

- **hvac** >= 2.1.0 - Primary Vault client library
- **ansible** - Module framework
- **requests** - HTTP client (used for EC2 IAM role authentication)

## Common Patterns

### Error Handling

```python
try:
    result = client.secrets.kv.read_secret_version(path=secret)
except InvalidPath:
    return {'rc': 1, 'failed': True, 'msg': 'Secret not found'}
```

### Version Support

- KV secrets engine v1 and v2 are both supported
- Use `version` parameter to specify KV version (default is v2)
- Use `mount_point` parameter for non-default mount points (default is `/secret`)

### Return Values

All modules should return:
- `changed` - Boolean indicating if state changed
- `rc` - Return code (0 for success)
- `failed` - Boolean indicating failure (optional, for failures)
- `msg` - Error message (for failures)
- Module-specific data fields

## CI/CD

GitHub Actions workflow (`.github/workflows/test.yml`):
- **Lint job**: Runs pycodestyle on Python 3.9
- **Tests job**: Runs tox functional tests on Python 3.9
- **Docs job**: Validates documentation generation

All jobs must pass for PR merge.
