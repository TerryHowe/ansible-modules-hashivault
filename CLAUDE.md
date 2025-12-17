# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See AGENTS.md for comprehensive project documentation including:
- Project overview and code structure
- Build, test, and development setup commands
- Code style conventions (PEP8, 120 char lines)
- Module patterns and security considerations
- Testing guidelines and CI/CD workflow

## Quick Reference

```bash
# Run all tests
tox

# Lint only
tox -e pep8

# Functional tests (requires Vault)
tox -e py39

# Development install
./link.sh
```
