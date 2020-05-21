#!/usr/bin/env python
from ansible.module_utils.hashivault import check_secrets_engines
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import check_pki_role
from ansible.module_utils.hashivault import compare_state
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_role
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Create/Update/Delete Role
description:
    - This module creates or updates the role definition.
    - Note that the `allowed_domains`, `allow_subdomains`, `allow_glob_domains`, and `allow_any_name` attributes are
      additive; between them nearly and across multiple roles nearly any issuing policy can be accommodated.
      `server_flag`, `client_flag`, and `code_signing_flag` are additive as well.
    - If a client requests a certificate that is not allowed by the CN policy in the role, the request is denied.
options:
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
    name:
        recuired: true
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
            - Collection of properties from pki role
              U(https://www.vaultproject.io/api-docs/secret/pki#create-update-role)
        suboptions:
            ttl:
                type: str
                description:
                    - Specifies the Time To Live value provided as a string duration with time suffix.
                    - Hour is the largest suffix.
                    - If not set, uses the system default value or the value of `max_ttl`, whichever is shorter.
            max_ttl:
                type: str
                description:
                    - Specifies the maximum Time To Live value provided as a string duration with time suffix.
                    - Hour is the largest suffix.
                    - If not set, defaults to the system maximum lease TTL.
            allow_localhost:
                type: bool
                default: true
                description:
                    - Specifies if clients can request certificates for `localhost` as one of the requested common
                      names.
                    - This is useful for testing and to allow clients on a single host to talk securely.
            allowed_domains:
                type: list
                description:
                    - Specifies the domains of the role.
                    - This is used with the `allow_bare_domains` and `allow_subdomains` options.
            allow_bare_domains:
                type: bool
                default: false
                description:
                    - Specifies if clients can request certificates matching the value of the actual domains themselves.
                    - e.g. if a configured domain set with `allowed_domains` is `example.com`, this allows clients to
                      actually request a certificate containing the name `example.com` as one of the DNS values on the
                      final certificate. In some scenarios, this can be considered a security risk.
            allow_subdomains:
                type: bool
                default: false
                description:
                    - Specifies if clients can request certificates with CNs that are subdomains of the CNs allowed by
                      the other role options. This includes wildcard subdomains.
                    - For example, an `allowed_domains` value of `example.com` with this option set to true will allow
                      `foo.example.com` and `bar.example.com` as well as `*.example.com`.
                    - This is redundant when using the `allow_any_name` option.
            allow_glob_domains:
                type: bool
                default: false
                description:
                    - Allows names specified in `allowed_domains` to contain glob patterns (e.g. `ftp*.example.com`)
                    - Clients will be allowed to request certificates with names matching the glob patterns.
            allow_any_name:
                type: bool
                default: false
                description:
                    - Specifies if clients can request any CN
                    - Useful in some circumstances, but make sure you understand whether it is appropriate for your
                      installation before enabling it.
            enforce_hostnames:
                type: bool
                default: true
                description:
                    - Specifies if only valid host names are allowed for CNs, DNS SANs, and the host part of email
                      addresses.
            allow_ip_sans:
                type: bool
                default: true
                description:
                    - Specifies if clients can request IP Subject Alternative Names
                    - No authorization checking is performed except to verify that the given values are valid IP
                      addresses.
            allowed_uri_sans:
                type: str
                description:
                    - Defines allowed URI Subject Alternative Names
                    - No authorization checking is performed except to verify that the given values are valid URIs
                    - This can be a comma-delimited list or a JSON string slice
                    - Values can contain glob patterns (e.g. `spiffe://hostname/*`).
            allowed_other_sans:
                type: str
                description:
                    - Defines allowed custom OID/UTF8-string SANs
                    - This can be a comma-delimited list or a JSON string slice, where each element has the same format
                      as OpenSSL `<oid>;<type>:<value>`, but the only valid type is `UTF8` or `UTF-8`
                    - The `value` part of an element may be a `*` to allow any value with that OID
                    - Alternatively, specifying a single `*` will allow any `other_sans` input. `server_flag`
                      `(bool)` Specifies if certificates are flagged for server use.
            server_flag:
                type: bool
                default: true
                description:
                    - Specifies if certificates are flagged for server use.
            client_flag:
                type: bool
                default: true
                description:
                    - Specifies if certificates are flagged for client use.
            code_signing_flag:
                type: bool
                default: false
                description:
                    - Specifies if certificates are flagged for code signing use.
            email_protection_flag:
                type: bool
                default: false
                description:
                    - Specifies if certificates are flagged for email protection use.
            key_type:
                type: str
                default: "rsa"
                description:
                    - Specifies the type of key to generate for generated private keys and the type of key expected for
                      submitted CSRs
                    - Currently, `rsa` and `ec` are supported, or when signing CSRs `any` can be specified to allow
                      keys of either type and with any bit size (subject to > 1024 bits for RSA keys).
            key_bits:
                type: int
                default: 2048
                description:
                    - Specifies the number of bits to use for the generated keys
                    - This will need to be changed for `ec` keys, e.g., 224 or 521.
            key_usage:
                type: list
                default: ["DigitalSignature", "KeyAgreement", "KeyEncipherment"]
                description:
                    - Specifies the allowed key usage constraint on issued certificates
                    - Valid values can be found at U(https://golang.org/pkg/crypto/x509/#KeyUsage) - simply drop the
                      `KeyUsage` part of the value
                    - Values are not case-sensitive
                    - To specify no key usage constraints, set this to an empty list.
            ext_key_usage:
                type: list
                description:
                    - Specifies the allowed extended key usage constraint on issued certificates
                    - Valid values can be found at U(https://golang.org/pkg/crypto/x509/#ExtKeyUsage) - simply drop the
                      `ExtKeyUsage` part of the value
                    - Values are not case-sensitive
                    - To specify no key usage constraints, set this to an empty list.
            ext_key_usage_oids:
                type: str
                description:
                    - A comma-separated string or list of extended key usage oids.
            use_csr_common_name:
                type: bool
                default: true
                description:
                    - When used with the CSR signing endpoint, the common name in the CSR will be used instead of taken
                      from the JSON data
                    - This does `not` include any requested SANs in the CSR; use `use_csr_sans` for that.
            use_csr_sans:
                type: bool
                default: true
                description:
                    - When used with the CSR signing endpoint, the subject alternate names in the CSR will be used
                      instead of taken from the JSON data
                    - This does `not` include the common name in the CSR; use `use_csr_common_name` for that.
            ou:
                type: list
                description:
                    - Specifies the OU (OrganizationalUnit) values in the subject field of issued certificates
            organization:
                type: list
                description:
                    - Specifies the O (Organization) values in the subject field of issued certificates
            country:
                type: list
                description:
                    - Specifies the C (Country) values in the subject field of issued certificates
            locality:
                type: list
                description:
                    - Specifies the L (Locality) values in the subject field of issued certificates
            province:
                type: list
                description:
                    - Specifies the ST (Province) values in the subject field of issued certificates
            street_address:
                type: list
                description:
                    - Specifies the Street Address values in the subject field of issued certificates
            postal_code:
                type: list
                description:
                    - Specifies the Postal Code values in the subject field of issued certificates
            serial_number:
                type: str
                description:
                    - Specifies the Serial Number, if any
                    - Otherwise Vault will generate a random serial for you
                    - If you want more than one, specify alternative names in the alt_names map using OID 2.5.4.5.
            generate_lease:
                type: bool
                default: false
                description:
                    - Specifies if certificates issued/signed against this role will have Vault leases attached to them
                    - Certificates can be added to the CRL by `vault revoke <lease_id>` when certificates are
                      associated with leases
                    - It can also be done using the `pki/revoke` endpoint
                    - However, when lease generation is disabled, invoking `pki/revoke` would be the only way to add
                      the certificates to the CRL.
            no_store:
                type: bool
                default: false
                description:
                    - If set, certificates issued/signed against this role will not be stored in the storage backend
                    - This can improve performance when issuing large numbers of certificates
                    - However, certificates issued in this way cannot be enumerated or revoked, so this option is
                      recommended only for certificates that are non-sensitive, or extremely short-lived
                    - This option implies a value of `false` for `generate_lease`.
            require_cn:
                type: bool
                default: true
                description:
                    - If set to false, makes the `common_name` field optional while generating a certificate.
            policy_identifiers:
                type: list
                description:
                    - A comma-separated string or list of policy OIDs.
            basic_constraints_valid_for_non_ca:
                type: bool
                default: false
                description:
                    - Mark Basic Constraints valid when issuing non-CA certificates.
            not_before_duration:
                type: duration
                default: "30s"
                description:
                    - Specifies the duration by which to backdate the NotBefore property.
extends_documentation_fragment:
    - hashivault
'''
EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - hashivault_pki_role:
        name: tester
        config:
            allow_subdomains: true

    - hashivault_pki_role:
        name: tester
        role_file: "/opt/vault/etc/roles/pki-tester.json"
        state: "present"
'''
normalize = {'list': list, 'str': str, 'dict': dict, 'bool': bool}


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=True, type='str')
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['mount_point'] = dict(required=False, type='str', default='pki')
    argspec['role_file'] = dict(required=False, type='str')
    argspec['config'] = dict(required=False, type='dict')

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_pki_role(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_role(module):
    params = module.params
    client = hashivault_auth_client(params)

    name = params.get('name').strip('/')
    mount_point = params.get('mount_point').strip('/')
    state = params.get('state')
    role_file = params.get('role_file')
    config = params.get('config')

    desired_state = {}
    exists = False

    if role_file:
        import json
        desired_state = json.loads(open(role_file, 'r').read())
    elif config:
        import yaml
        doc = yaml.safe_load(DOCUMENTATION)
        args = doc.get('options').get('config').get('suboptions').items()
        for key, value in args:
            arg = config.get(key)
            if arg is not None:
                try:
                    desired_state[key] = normalize[value.get('type')](arg)
                except Exception:
                    return {'changed': False, 'failed': True,
                            'msg': 'config item \'{}\' has wrong data fromat'.format(key)}

    # check if engine is enabled
    changed, err = check_secrets_engines(module, client)
    if err:
        return err

    current_state = check_pki_role(name=name, mount_point=mount_point, client=client)
    if current_state:
        exists = True

    if (exists and state == 'absent') or (not exists and state == 'present'):
        changed = True

    # compare current_state to desired_state
    if exists and state == 'present' and not changed:
        changed = not compare_state(desired_state, current_state)

    # make the changes!
    if changed and state == 'present' and not module.check_mode:
        client.secrets.pki.create_or_update_role(name=name, mount_point=mount_point, extra_params=desired_state)

    elif changed and state == 'absent' and not module.check_mode:
        client.secrets.pki.delete_role(name=name, mount_point=mount_point)

    return {'changed': changed}


if __name__ == '__main__':
    main()
