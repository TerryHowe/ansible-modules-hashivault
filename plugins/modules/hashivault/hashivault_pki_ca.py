#!/usr/bin/env python
from ansible.module_utils.hashivault import hashivault_auth_client
from ansible.module_utils.hashivault import hashivault_argspec
from ansible.module_utils.hashivault import hashivault_init
from ansible.module_utils.hashivault import hashiwrapper

ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'version': '1.1'}
DOCUMENTATION = r'''
---
module: hashivault_pki_ca
version_added: "4.5.0"
short_description: Hashicorp Vault PKI Generate Root/Intermediate
description:
    - 'WARNING: if king is `intermediate` and signed CSR have not been inported back to vault, module will regenerate
      private key and create new CSR.'
    - This module generates a new private key and a CSR for signing or a new self-signed CA certificate and private key.
    - If using Vault as a root, and for many other CAs, the various parameters on the final certificate are set at
      signing time and may or may not honor the parameters set here.
    - This will overwrite any previously existing CA private key.
    - This is mostly meant as a helper function, and not all possible parameters that can be set in a CSR are supported.
options:
    mount_point:
        default: pki
        description:
            - location where secrets engine is mounted. also known as path
    type:
        type: str
        choices: ["exported", "internal"]
        default: internal
        description:
            - Specifies the type of the root to create, If `exported`, the private key will be returned in the
              response;
            - If it is `internal` the private key will not be returned and cannot be retrieved later.
    common_name:
        type: str
        description:
            - Specifies the requested CN for the certificate. [required]
    kind:
        type: str
        choices: ["root", "intermediate"]
        default: root
        description:
            - Specifies the kind of CA certificate.
    state:
        type: str
        choices: ["present", "absent"]
        default: present
        description:
            - Do you want for this config to be present or absent
    config:
        description:
            - Collection of properties for pki generate root. Ref.
              U(https://www.vaultproject.io/api-docs/secret/pki#generate-root)
        type: dict
        suboptions:
            alt_names:
                type: str
                description:
                    - Specifies the requested Subject Alternative Names, in a comma-delimited list.
                    - These can be host names or email addresses; they will be parsed into their respective fields.
            ip_sans:
                type: str
                description:
                    - Specifies the requested IP Subject Alternative Names, in a comma-delimited list.
            uri_sans:
                type: str
                description:
                    - Specifies the requested URI Subject Alternative Names, in a comma-delimited list.
            other_sans:
                type: str
                description:
                    - Specifies custom OID/UTF8-string SANs.
                    - These must match values specified on the role in `allowed_other_sans` (see role creation for
                      allowed_other_sans globbing rules).
                    - The format is the same as OpenSSL `<oid>;<type>:<value>` where the only current valid type is
                      `UTF8`
                    - This can be a comma-delimited list or a JSON string slice.
            ttl:
                type: str
                description:
                    - Specifies the requested Time To Live (after which the certificate will be expired).
                    - This cannot be larger than the engine's max (or, if not set, the system max).
            format:
                type: str
                default: "pem"
                choice: ["pem", "der", "pem_bundle"]
                description:
                    - Specifies the format for returned data.
                    - If `der`, the output is base64 encoded.
                    - If `pem_bundle`, the `certificate` field will contain the private key (if exported) and
                      certificate, concatenated;
                    - if the issuing CA is not a Vault-derived self-signed root, this will be included as well.
            private_key_format:
                type: str
                default: der
                description:
                    - Specifies the format for marshaling the private key.
                    - Defaults to `der` which will return either base64-encoded DER or PEM-encoded DER, depending on
                      the value of `format`.
                    - The other option is `pkcs8` which will return the key marshalled as PEM-encoded PKCS8
            key_type:
                type: str
                default: "rsa"
                choice: ["rsa", "ec"]
                description:
                    - Specifies the desired key type.
            key_bits:
                type: int
                default: 2048
                description:
                    - Specifies the number of bits to use
            max_path_length:
                type: int
                default: -1
                description:
                    - Specifies the maximum path length to encode in the generated certificate.
                    - A limit of `-1` means no limit.
                    - Unless the signing certificate has a maximum path length set, in which case the path length is set
                      to one less than that of the signing certificate.
                    - A limit of `0` means a literal path length of zero.
            exclude_cn_from_sans:
                type: bool
                default: false
                description:
                    - If set, the given `common_name` will not be included in DNS or Email Subject Alternate Names (as
                      appropriate).
                    - Useful if the CN is not a hostname or email address, but is instead some human-readable
                      identifier.
            permitted_dns_domains:
                type: list
                description:
                    - A list containing DNS domains for which certificates are allowed to be issued or signed by this CA
                      certificate.
                    - Note that subdomains are allowed, as per U(https://tools.ietf.org/html/rfc5280#section-4.2.1.10).
            ou:
                type: list
                description:
                    - Specifies the `OU` (OrganizationalUnit) values in the subject field of the resulting certificate.
            organization:
                type: list
                description:
                    - Specifies the `O` (Organization) values in the subject field of the resulting certificate.
            country:
                type: list
                description:
                    - Specifies the `C` (Country) values in the subject field of the resulting certificate.
            locality:
                type: list
                description:
                    - Specifies the `L` (Locality) values in the subject field of the resulting certificate.
            province:
                type: list
                description:
                    - Specifies the `ST` (Province) values in the subject field of the resulting certificate.
            street_address:
                type: list
                description:
                    - Specifies the Street Address values in the subject field of the resulting certificate.
            postal_code:
                type: list
                description:
                    - Specifies the Postal Code values in the subject field of the resulting certificate.
            serial_number:
                type: string
                description:
                    - Specifies the Serial Number, if any.
                    - Otherwise Vault will generate a random serial for you.
                    - If you want more than one, specify alternative names in the alt_names map using OID 2.5.4.5.
extends_documentation_fragment:
    - hashivault
'''
EXAMPLES = r'''
---
- hosts: localhost
  tasks:
    - name: Delete Root
      hashivault_pki_ca:
        common_name: my common name
'''


def main():
    argspec = hashivault_argspec()
    argspec['common_name'] = dict(required=True, type='str')
    argspec['mount_point'] = dict(required=False, type='str', default='pki')
    argspec['state'] = dict(required=False, type='str', default='present', choices=['present', 'absent'])
    argspec['kind'] = dict(required=False, type='str', default='root', choices=['root', 'intermediate'])
    argspec['type'] = dict(required=False, type='str', default='internal', choices=['internal', 'exported'])
    argspec['config'] = dict(required=False, type='dict', default={})

    supports_check_mode = True

    module = hashivault_init(argspec, supports_check_mode)
    result = hashivault_pki_ca(module)

    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


@hashiwrapper
def hashivault_pki_ca(module):
    params = module.params
    client = hashivault_auth_client(params)

    common_name = params.get('common_name')
    mount_point = params.get('mount_point').strip('/')
    state = params.get('state')
    kind = params.get('kind')
    type = params.get('type')
    config = params.get('config')

    exists = False
    changed = False

    # check if CA certificate exists
    if client.secrets.pki.read_ca_certificate(mount_point=mount_point):
        # WARNING: if king is `intermediate` and signed CSR have not been inported back to vault, module will regenerate
        # private key and create new CSR. This check will not see that CA exist although private key is generate, and
        # CSR might be in proccess to be signed.
        exists = True

    if (exists and state == 'absent') or (not exists and state == 'present'):
        changed = True

    result = {"changed": changed, "rc": 0}

    # make the changes!
    if changed and state == 'present' and not module.check_mode:
        if kind == 'root':
            resp = client.secrets.pki.generate_root(type=type, common_name=common_name, extra_params=config,
                                                    mount_point=mount_point)
            result['data'] = resp.get('data')
            if resp.get('warnings'):
                result['warnings'] = resp.get('warnings')
        elif kind == 'intermediate':
            resp = client.secrets.pki.generate_intermediate(type=type, common_name=common_name, extra_params=config,
                                                            mount_point=mount_point)
            result['data'] = resp.get('data')
            if resp.get('warnings'):
                result['warnings'] = resp.get('warnings')

    elif changed and state == 'absent' and not module.check_mode:
        client.secrets.pki.delete_root(mount_point=mount_point)

    return result


if __name__ == '__main__':
    main()
