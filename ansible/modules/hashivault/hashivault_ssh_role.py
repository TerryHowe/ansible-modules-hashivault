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
module: hashivault_ssh_role
version_added: "4.7.0"
short_description: Hashicorp Vault SSH Create/Update/Delete Role
description:
    - This module creates or updates the role definition.
    - Note that the `allowed_domains`, `allow_subdomains`, `allow_glob_domains`, and `allow_any_name` attributes are
      additive; between them nearly and across multiple roles nearly any issuing policy can be accommodated.
      `server_flag`, `client_flag`, and `code_signing_flag` are additive as well.
    - If a client requests a certificate that is not allowed by the CN policy in the role, the request is denied.
options:
    mount_point:
        default: ssh
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
            - Collection of properties from ssh role
              U(https://www.vaultproject.io/api/secret/ssh#create-role)
        suboptions:
            key:
                type: str
                default: ""
                description:
                    - Specifies the name of the registered key in Vault. Before
                      creating the role, use the `keys/` endpoint to create a
                      named key. This is required for "Dynamic Key" type.
            admin_user:
                type: str
                default: ""
                description:
                    - Specifies the admin user at remote host. The shared key
                      being registered should be for this user and should have
                      root or sudo privileges. Every time a dynamic credential
                      is generated for a client, Vault uses this admin username
                      to login to remote host and install the generated
                      credential. This is required for Dynamic Key type.
            default_user:
                type: str
                default: ""
                description:
                    - Specifies the default username for which a credential
                      will be generated. When the endpoint `creds/` is used
                      without a username, this value will be used as default
                      username. Its recommended to create individual roles for
                      each username to ensure absolute isolation between
                      usernames. This is required for Dynamic Key type and OTP
                      type.
                    - For the CA type, if you wish this to be a valid
                      principal, it must also be in `allowed_users`.
            cidr_list:
                type: str
                default: ""
                description:
                    - Specifies a comma separated list of CIDR blocks for which
                      the role is applicable for. It is possible that a same
                      set of CIDR blocks are part of multiple roles. This is a
                      required parameter, unless the role is registered under
                      the `/config/zeroaddress` endpoint.
            exclude_cidr_list:
                type: str
                default: ""
                description:
                    - Specifies a comma-separated list of CIDR blocks. IP
                      addresses belonging to these blocks are not accepted by
                      the role. This is particularly useful when big CIDR
                      blocks are being used by the role and certain parts need
                      to be kept out.
            port:
                type: int
                default: 22
                description:
                    - Specifies the port number for SSH connection. Port number
                      does not play any role in OTP generation. For the `otp`
                      secrets engine type, this is just a way to inform the
                      client about the port number to use. The port number will
                      be returned to the client by Vault along with the OTP.
            key_type:
                type: str
                choices: ["otp", "dynamic", "ca"]
                required: true
                description:
                    - Specifies the type of credentials generated by this role.
                      This can be either `otp`, `dynamic` or `ca`.
            key_bits:
                type: int
                choices: [1024, 2048]
                default: 1024
                description:
                    - Specifies the length of the RSA dynamic key in bits. This
                      can be either `1024` or `2048`.
            install_script:
                type: str
                default: ""
                description:
                    - Specifies the script used to install and uninstall public
                      keys in the target machine. Defaults to the built-in
                      script.
            allowed_users:
                type: str
                default: ""
                description:
                    - |-
                      If this option is not specified, or if it is `*`, the
                      client can request a credential for any valid user at the
                      remote host, including the admin user. If only certain
                      usernames are to be allowed, then this list enforces it.
                      If this field is set, then credentials can only be
                      created for `default_user` and usernames present in this
                      list. Setting this option will enable all the users with
                      access to this role to fetch credentials for all other
                      usernames in this list. When `allowed_users_template` is
                      set to `true`, this field can contain an identity template
                      with any prefix or suffix, like
                      `ssh-{{identity.entity.id}}-user`. Use with caution. N.B.:
                      if the type is `ca`, an empty list does not allow any
                      user; instead you must use `*` to enable this behavior.
            allowed_users_template:
                type: bool
                default: false
                description:
                    - If set, `allowed_users` can be specified using identity
                      template policies. Non-templated users are also
                      permitted.
            allowed_domains:
                type: str
                default: ""
                description:
                    - The list of domains for which a client can request a host
                      certificate. If this option is explicitly set to `"*"`,
                      then credentials can be created for any domain. See also
                      `allow_bare_domains` and `allow_subdomains`.
            key_option_specs:
                type: str
                default: ""
                description:
                    - |-
                      Specifies a comma separated option specification which
                      will be prefixed to RSA keys in the remote host's
                      authorized_keys file. N.B.: Vault does not check this
                      string for validity.
            ttl:
                type: str
                default: ""
                description:
                    - Specifies the Time To Live value provided as a string
                      duration with time suffix. Hour is the largest suffix. If
                      not set, uses the system default value or the value of
                      `max_ttl`, whichever is shorter.
            max_ttl:
                type: str
                default: ""
                description:
                    - Specifies the maximum Time To Live provided as a string
                      duration with time suffix. Hour is the largest suffix. If
                      not set, defaults to the system maximum lease TTL.
            allowed_critical_options:
                type: str
                default: ""
                description:
                - Specifies a comma-separated list of critical options that
                  certificates can have when signed. To allow any critical
                  options, set this to an empty string. Will default to
                  allowing any critical options.
            allowed_extensions:
                type: str
                default: ""
                description:
                    - Specifies a comma-separated list of extensions that
                      certificates can have when signed. To allow a user to
                      specify any extension, set this to `"*"`. If not set, users
                      will not be allowed to specify extensions and will get
                      the extensions specified within `default_extensions`. For
                      the list of extensions, take a look at the sshd manual's
                      U(https://man.openbsd.org/sshd#AUTHORIZED_KEYS_FILE_FORMAT)
                      `AUTHORIZED_KEYS FILE FORMAT` section. You should add a
                      `permit-` before the name of extension to allow it.
            default_critical_options:
                type: dict
                default: null
                description:
                    - Specifies a map of critical options certificates should
                      have if none are provided when signing. This field takes
                      in key value pairs in JSON format. Note that these are
                      not restricted by `allowed_critical_options`. Defaults to
                      none.
            default_extensions:
                type: dict
                default: null
                description:
                    - Specifies a map of extensions certificates should have if
                      none are provided when signing. This field takes in key
                      value pairs in JSON format. Note that these are not
                      restricted by `allowed_extensions`. Defaults to none.
            allow_user_certificates:
                type: bool
                default: false
                description:
                    - Specifies if certificates are allowed to be signed for
                      use as a 'user'.
            allow_host_certificates:
                type: bool
                default: false
                description:
                    - Specifies if certificates are allowed to be signed for
                      use as a 'host'.
            allow_bare_domains:
                type: bool
                default: false
                description:
                    - Specifies if host certificates that are requested are
                      allowed to use the base domains listed in
                      `allowed_domains`, e.g. "example.com". This is a separate
                      option as in some cases this can be considered a security
                      threat.
            allow_subdomains:
                type: bool
                default: false
                description:
                    - Specifies if host certificates that are requested are
                      allowed to be subdomains of those listed in
                      `allowed_domains`, e.g. if "example.com" is part of
                      `allowed_domains`, this allows "foo.example.com".
            allow_user_key_ids:
                type: bool
                default: false
                description:
                    - Specifies if users can override the key ID for a signed
                      certificate with the "key_id" field. When false, the key
                      ID will always be the token display name. The key ID is
                      logged by the SSH server and can be useful for auditing.
            key_id_format:
                type: str
                default: ""
                description:
                    - |-
                      When supplied, this value specifies a custom format for
                      the key id of a signed certificate. The following
                      variables are available for use: '{{token_display_name}}'
                      - The display name of the token used to make the request.
                      '{{role_name}}' - The name of the role signing the
                      request. '{{public_key_hash}}' - A SHA256 checksum of
                      the public key that is being signed. e.g.
                      "custom-keyid-{{token_display_name}}"
            allowed_user_key_lengths:
                type: dict
                default: null
                description:
                    - Specifies a map of ssh key types and their expected sizes
                      which are allowed to be signed by the CA type.
            algorithm_signer:
                type: str
                choices: ["", "ssh-rsa", "rsa-sha2-256", "rsa-sha2-512"]
                default: ""
                description:
                    - Algorithm to sign keys with. Valid values are `ssh-rsa`,
                      `rsa-sha2-256`, and `rsa-sha2-512`. This value may be left
                      blank to use the signer's default algorithm, and must be
                      left blank for CA key types other than RSA. Note that
                      `ssh-rsa` is now considered insecure and is not supported
                      by current OpenSSH versions.
extends_documentation_fragment:
    - hashivault
"""
EXAMPLES = r"""
---
- hosts: localhost
  tasks:
    - hashivault_ssh_role:
        name: tester
        config:
            key_type: ca
            allowed_users: tester
            default_user: tester

    - hashivault_ssh_role:
        name: tester
        role_file: "/opt/vault/etc/roles/ssh-tester.json"
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
    argspec["mount_point"] = dict(required=False, type="str", default="ssh")
    argspec["role_file"] = dict(required=False, type="str")
    argspec["config"] = dict(required=False, type="dict")

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_ssh_role(module)

    if result.get("failed"):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_ssh_role(module):
    params = module.params
    client = hashivault_auth_client(params)

    name = params.get("name").strip("/")
    mount_point = params.get("mount_point").strip("/")
    state = params.get("state")
    role_file = params.get("role_file")
    config = params.get("config")
    path = f"roles/{name}"

    desired_state = {}
    exists = False

    if role_file:
        with open(role_file, "rt") as fp:
            desired_state = json.safe_load(fp.read())
    elif config:
        desired_state = copy.deepcopy(config)

    changed = False

    try:
        current_state = client.secrets.pki.read_role(
            name=name, mount_point=mount_point
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
            data = {}

            doc = yaml.safe_load(DOCUMENTATION)
            args = doc.get("options").get("config").get("suboptions").items()
            for key, value in args:
                arg = desired_state.get(key)
                if arg is not None:
                    try:
                        data[key] = normalize[value.get("type")](arg)
                    except Exception:
                        return {
                            "changed": False,
                            "failed": True,
                            "msg": "config item '{}' has wrong data format".format(key),
                        }
            # create or update
            client.secrets.kv.v1.create_or_update_secret(
                mount_point=mount_point,
                path=path,
                secret=data,
            )
    elif changed and state == "absent":
        if not module.check_mode:
            # delete
            client.secrets.kv.v1.delete_secret(
                mount_point=mount_point,
                path=path,
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
