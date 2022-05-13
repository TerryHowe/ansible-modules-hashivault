#!/usr/bin/env python

import copy

import yaml

from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper


ANSIBLE_METADATA = {
    "status": ["preview"],
    "supported_by": "community",
    "version": "1.1",
}
DOCUMENTATION = r"""
---
module: hashivault_token_role
version_added: "4.7.0"
short_description: Hashicorp Vault Token Create/Update/Delete Role
description:
    - This module creates or updates the token role definition.
options:
    mount_point:
        default: token
        description:
            - location where secrets engine is mounted. also known as path
    name:
        required: true
        description:
            - Specifies the name of the role to create.
    role_file:
        description:
            - file with a json object containing play parameters. pass all params but name, state, mount_point which
              stay in the ansible play
    state:
        description:
            - Do you want for this config to be present or absent
        choices: ["present", "absent"]
        default: present
    config:
        type: dict
        description:
            - Collection of properties from token role
              U(https://www.vaultproject.io/api-docs/auth/token#create-update-token-role)
        suboptions:
            allowed_policies:
                type: list
                description:
                - If set, tokens can be created with any subset of the policies
                  in this list, rather than the normal semantics of tokens being
                  a subset of the calling token's policies. The parameter is a
                  comma-delimited string of policy names. If at creation time
                  `no_default_policy` is not set and `"default"` is not
                  contained in `disallowed_policies` or glob matched in
                  `disallowed_policies_glob`, the `"default"` policy will be
                  added to the created token automatically.
            disallowed_policies:
                type: list
                description:
                - If set, successful token creation via this role will require
                  that no policies in the given list are requested. The parameter
                  is a comma-delimited string of policy names. Adding `"default"`
                  to this list will prevent `"default"` from being added
                  automatically to created tokens.
            allowed_policies_glob:
                type: list
                description:
                - If set, tokens can be created with any subset of glob matched
                  policies in this list, rather than the normal semantics of
                  tokens being a subset of the calling token's policies. The
                  parameter is a comma-delimited string of policy name globs.
                  If at creation time `no_default_policy` is not set and
                  `"default"` is not contained in `disallowed_policies` or glob
                  matched in `disallowed_policies_glob`, the `"default"` policy
                  will be added to the created token automatically. If combined
                  with `allowed_policies` policies need to only match one of the
                  two lists to be permitted. Note that unlike `allowed_policies`
                  the policies listed in `allowed_policies_glob` will not be
                  added to the token when no policies are specified in the
                  call to `/auth/token/create/:role_name`.
            disallowed_policies_glob:
                type: list
                description:
                - If set, successful token creation via this role will require
                  that no requested policies glob match any of policies in this
                  list. The parameter is a comma-delimited string of policy
                  name globs. Adding any glob that matches `"default"` to this
                  list will prevent `"default"` from being added automatically
                  to created tokens. If combined with `disallowed_policies`
                  policies need to only match one of the two lists to be blocked.
            orphan:
                type: bool
                default: false
                description:
                - If `true`, tokens created against this policy will be orphan
                  tokens (they will have no parent). As such, they will not be
                  automatically revoked by the revocation of any other token.
            renewable:
                type: bool
                default: true
                description:
                - Set to `false` to disable the ability of the token to be
                  renewed past its initial TTL. Setting the value to `true`
                  will allow the token to be renewable up to the system/mount
                  maximum TTL.
            path_suffix:
                type: str
                description:
                - If set, tokens created against this role will have the given
                  suffix as part of their path in addition to the role name.
                  This can be useful in certain scenarios, such as keeping the
                  same role name in the future but revoking all tokens created
                  against it before some point in time. The suffix can be
                  changed, allowing new callers to have the new suffix as part
                  of their path, and then tokens with the old suffix can be
                  revoked via `/sys/leases/revoke-prefix`.
            allowed_entity_aliases:
                type: list
                description:
                - String or JSON list of allowed entity aliases. If set,
                  specifies the entity aliases which are allowed to be used
                  during token generation. This field supports globbing.
                  Note that `allowed_entity_aliases` is not case sensitive.
            token_bound_cidrs:
                type: list
                description:
                - List of CIDR blocks; if set, specifies blocks of IP
                  addresses which can authenticate successfully, and ties the
                  resulting token to these blocks as well.
            token_explicit_max_ttl:
                type: str
                description:
                - If set, will encode an explicit max TTL onto the token.
                  This is a hard cap even if token_ttl and token_max_ttl would
                  otherwise allow a renewal.
            token_no_default_policy:
                type: bool
                default: false
                description:
                - If set, the `default` policy will not be set on generated
                  tokens; otherwise it will be added to the policies set in
                  `token_policies`.
            token_num_uses:
                type: int
                default: 0
                description:
                - The maximum number of times a generated token may be used
                  (within its lifetime); 0 means unlimited. If you require
                  the token to have the ability to create child tokens, you
                  will need to set this value to 0.
            token_period:
                type: str
                default: ""
                description:
                - The period, if any, to set on the token.
            token_type:
                type: str
                default: ""
                description:
                - |-
                  The type of token that should be generated. Can be `service`,
                  `batch`, or `default` to use the mount's tuned default (which
                  unless changed will be `service` tokens). For token store
                  roles, there are two additional possibilities:
                  `default-service` and `default-batch` which specify the type
                  to return unless the client requests a different type at
                  generation time.
extends_documentation_fragment:
    - hashivault
"""
EXAMPLES = r"""
---
- hosts: localhost
  tasks:
    - hashivault_token_role:
        name: tester-bot
        config:
          allowed_policies:
            - tester-bot

    - hashivault_token_role:
        name: tester-bot
        role_file: "/opt/vault/etc/roles/token-tester-bot.json"
        state: "present"
"""
normalize = {
    "list": list,
    "str": str,
    "dict": dict,
    "bool": bool,
    "int": int,
    "duration": str,
}


def main():
    argspec = hashivault_argspec()
    argspec["name"] = dict(required=True, type="str")
    argspec["state"] = dict(
        required=False, type="str", default="present", choices=["present", "absent"]
    )
    argspec["mount_point"] = dict(required=False, type="str", default="token")
    argspec["role_file"] = dict(required=False, type="str")
    argspec["config"] = dict(required=False, type="dict")

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_token_role(module)

    if result.get("failed"):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_token_role(module):
    params = module.params
    client = hashivault_auth_client(params)

    name = params.get("name").strip("/")
    mount_point = params.get("mount_point").strip("/")
    state = params.get("state")
    role_file = params.get("role_file")
    config = params.get("config")

    desired_state = {}
    exists = False

    if role_file:
        with open(role_file, "rt") as fp:
            desired_state = json.safe_load(fp.read())
    elif config:
        desired_state = copy.deepcopy(config)

    changed = False

    try:
        current_state = client.auth.token.read_role(
            role_name=name, mount_point=mount_point
        ).get("data")
    except Exception:
        current_state = {}

    if current_state:
        exists = True

    if (exists and state == "absent") or (not exists and state == "present"):
        changed = True

    # compare current_state to config (desired_state before normalization)
    if exists and state == "present" and not changed:
        # Update all keys not present in the desired_state with data from the
        # current_state, to ensure a proper diff output.
        for key in current_state:
            if desired_state.get(key) is None:
                desired_state[key] = current_state[key]

        changed = desired_state != current_state

    # make the changes!
    if changed and state == "present":
        if not module.check_mode:
            # Before posting the desired state to the vault api we need to
            # normalize some keys. This is a quirk of the vault api that it
            # expects a different data format in the PUT/POST endpoint than
            # it returns in the GET endpoint.
            extra_params = {}

            doc = yaml.safe_load(DOCUMENTATION)
            args = doc.get("options").get("config").get("suboptions").items()
            for key, value in args:
                arg = desired_state.get(key)
                if arg is not None:
                    try:
                        extra_params[key] = normalize[value.get("type")](arg)
                    except Exception:
                        return {
                            "changed": False,
                            "failed": True,
                            "msg": "config item '{}' has wrong data format".format(key),
                        }
            # create or update
            api_path = f"/v1/auth/{mount_point}/roles/{name}"
            client.auth.token._adapter.post(url=api_path, json=extra_params)
    elif changed and state == "absent":
        if not module.check_mode:
            # delete
            client.auth.token.delete_role(
                role_name=name,
                mount_point=mount_point,
            )
        # after deleting it the item is no more
        desired_state = {}

    return {
        "changed": changed,
        "diff": {
            "before": current_state,
            "after": desired_state,
        },
    }


if __name__ == "__main__":
    main()
