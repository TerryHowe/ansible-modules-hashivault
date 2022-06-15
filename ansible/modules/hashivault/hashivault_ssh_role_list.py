#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper
from hvac.exceptions import InvalidPath

ANSIBLE_METADATA = {
    "status": ["preview"],
    "supported_by": "community",
    "version": "1.1",
}
DOCUMENTATION = r"""
---
module: hashivault_ssh_role_list
version_added: "4.7.0"
short_description: Hashicorp Vault SSH List Roles
description:
    - This module returns a list of available roles.
    - Only the role names are returned, not any values.
options:
    mount_point:
        default: ssh
        description:
            - location where secrets engine is mounted. also known as path
extends_documentation_fragment:
    - hashivault
"""
EXAMPLES = r"""
---
- hosts: localhost
  tasks:
    - hashivault_ssh_role_list:
        mount_point: ssh
      register: roles_list
    - debug: msg="{{ roles_list.data }}"
"""
RETURN = r"""
---
data:
    description: list of roles, if ssh engine has no roles will return empty list
    returned: success
    type: list
"""


def main():
    argspec = hashivault_argspec()
    argspec["mount_point"] = dict(required=False, type="str", default="ssh")

    module = hashivault_init(argspec, supports_check_mode=True)
    result = hashivault_pki_role_list(module)

    if result.get("failed"):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_role_list(module):
    params = module.params
    client = hashivault_auth_client(params)

    mount_point = params.get("mount_point").strip("/")

    try:
        return {
            "data": client.secrets.kv.v1.list_secrets(
                mount_point=mount_point,
                path="roles",
            )
            .get("data")
            .get("keys")
        }
    except InvalidPath as exc:
        if len(exc.errors) == 0:  # Path is valid but no roles exist.
            return {"data": []}
        return {"failed": True, "data": [], "msg": str(exc)}
    except Exception as exc:
        return {"failed": True, "data": [], "msg": str(exc)}


if __name__ == "__main__":
    main()
