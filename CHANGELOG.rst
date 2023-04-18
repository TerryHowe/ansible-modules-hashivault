Changelog
=========


5.1.0 (2023-04-18)
------------------
- Refactor policy module. [Cees Moerkerken]
- Add diff, fixes #439. [Cees Moerkerken]
- Add path to return values. [Cees Moerkerken]
- Fix line length linting. [Cees Moerkerken]
- Only call enable or tune when changed. add comments. [Cees Moerkerken]
- Add result to return values, fixes #435. [Cees Moerkerken]
- Add diff, fixes #436. [Cees Moerkerken]
- Replace whitelist_externals with allowlist_externals. [Cees
  Moerkerken]
- Prevent keyerror on inconsistencies between the current and desired
  state. [Cees Moerkerken]
- Add diff and enable check mode support. [Cees Moerkerken]
- Warn user when an unknown value is processed by the option
  normalization. [Benjamin Demarteau]
- Extract option normalisation to module_utils and reverse logic to
  allow for unknown options. [Benjamin Demarteau]
- Create SECURITY.md. [Terry Howe]


5.0.0 (2022-11-08)
------------------
- Remove deprecated modules. [Terry Howe]
  * hashivault_approle_role_create
  * hashivault_approle_role_secret_create
  * hashivault_approle_role_secret_delete
  * hashivault_audit_enable
  * hashivault_auth_enable
  * hashivault_aws_ec2_role_create
  * hashivault_mount_tune
  * hashivault_policy_delete
  * hashivault_policy_set
  * hashivault_policy_set_from_file
  * hashivault_secret_disable
  * hashivault_secret_enable
  * hashivault_userpass_create
  * hashivault_userpass_delete
- Changes for hvac 1.x. [Terry Howe]
- Breaking Changes:
  * hashivault_approle_role_secret removed wrap_ttl for now
  * hashivault_generate_root_init otp added
  * hashivault_token_create removed lease and orphan (use no_parent)
  * ansible 5 only now



4.7.1 (2022-11-07)
------------------
- Disable hvac 1.x support for now. [Terry Howe]
- Update configuration. [Terry Howe]
- Add idempotency test to test_ldap_group. [Matt Harlum]
- Fix "enable ldap authentication" in test_ldap_group. [Matt Harlum]
- Fixup idempotency of hashivault_auth_ldap. [Matt Harlum]
- Add self_renew for hashivault_token_renew. [Terry Howe]
- Fix PKI tests from new hvac. [Terry Howe]


4.7.0 (2022-06-19)
------------------
- Add a hashivault_ssh_role_list module. [Szymon Soloch]
- Add a hashivault_ssh_role module. [Szymon Soloch]
- Add a hashivault_token_role_list module. [Szymon Soloch]
- Add a hashivault_token_role module. [Szymon Soloch]
- Get better auth method tests. [Terry Howe]
- Fix auth_method idempotency. [ayav09]
- Fix tests. [Terry Howe]
- Fix docs build. [Terry Howe]
- Fix state comparison of lists. [Jarno Antikainen]


4.6.8 (2022-02-19)
------------------
- Allow create nonexistent secret when state is update. [Pavel Ezhov]


4.6.7 (2022-02-08)
------------------
- Fix db_secret_engine_config idempotency for password policy and non-
  default mount point. [ayav09]
- Fix hashivault_db_secret_engine_role delete idempotency. [ayav09]
- Readme updates. [ayav09]
- Specify type for states. [Terry Howe]


4.6.6 (2022-02-06)
------------------
- Set no_log for a few things. [Terry Howe]
- Pep8 fixes. [ayav09]
- Fix root rotation statements in connection details. [ayav09]
- Remove unneeded lstrip. [Terry Howe]
- Fix hashivault_list URL with lstrip. [Gregory Fredj]

  Right now it is using `lstrip('metadata/')` and if the path contains any letter in "metadata" it will be removed. lstrip() isn't the function to use but rather replace and only once.


4.6.5 (2022-01-11)
------------------
- Return secret version when reading kv v2 secret. [Albin Kerouanton]
- Transform lease TTLs into ints. [Albin Kerouanton]
- Removed static role_type oidc. [Alex Vermulst]
- Advise against strings in hashivault_pki_role params. [Albin
  Kerouanton]
- Fix docs build. [Terry Howe]
- Argspec['password_policy'] [Piotr Grabowski]
- Password_policy. [Piotr Grabowski]
- Pass cas value to hvac when kv-v2 backend is used. [Albin Kerouanton]
- Rekey docs clarification. [Terry Howe]
- Work if no token_bound_cidr. [Terry Howe]
- Remove tests for deprecated modules. [Terry Howe]
- Reduce tests to 3.9. [Terry Howe]
- Introduce support for PKI allowed_domains_template. [Eric Trexel]
- Add token_type option to k8s_auth_role. [ayav09]
- Initial github actions workflow. [ayav09]
- Pep8 fixes. [ayav09]
- Replace deprecated hvac userpass methods. [ayav09]


4.6.4 (2021-08-26)
------------------
- Require Ansible 4. [Terry Howe]
- Add pepy. [Terry Howe]
- Fix pki role not_before_duration. [ayav09]


4.6.3 (2021-07-25)
------------------
- Fix list tests. [Terry Howe]
- Allow to list secrets in subpath (issue #324) [Didier Fournout]
- Fix unit testing. [Lord-Y]
- Fix ldap tests. [Terry Howe]
- Add kv2 idempotent test. [Terry Howe]
- Use list_secrets function by default for modern Vault versions. [Pavlo
  Zinchuk]
- Update hashivault_auth_ldap.py. [tp6783]
- Fix typo in hashivault_auth_method. [Adrian Moisey]
- Add optional provider_config dict. [Marko Doda]
- Update readme. [Terry Howe]
- Fix hashivault_audit_list `changed` state. [Piotr Śliwka]
- Updated approle authentication. [Ivan Kurnosov]
- Update hashivault_userpass example to use newer module.[Lander Visterin]
- Documentation fix. [Torinthiel]


4.6.2 (2020-11-03)
------------------
- Support verified rekeys. [Torinthiel]


4.6.1 (2020-11-03)
------------------
- Update docs for hashivault_secret and lookup. [Terry Howe]
- Use v1 call for hashivault_write. [Terry Howe]
- Add metadata read to kv2 list. [Terry Howe]
- Add update support to hashivault_secret. [Terry Howe]
- Get rid of warning suppression. [Terry Howe]
- Add parameters to lookup plugin. [Terry Howe]
- Add hashivault_secret. [Terry Howe]
- Fix README format. [Terry Howe]


4.6.0 (2020-10-30)
------------------
- Hashivault_delete: Permanently delete secret for v2. [wolfmah]
- Remove warning oppression. [Terry Howe]
- Create common compare with ttl support. [Terry Howe]
- Get rid of check_pki_role. [Terry Howe]
- Add logic to detect pem_keys change in k8s auth config. [tottoto]
- Add ignore list to detect changes of k8s auth config. [tottoto]
- Added kv2 secret engine options. [Tomasz Napierala]
- Fix pki role for int. [Terry Howe]
- Fix incompatible approle parameter. [Terry Howe]
- Refactor the way to get oidc auth field. [tottoto]
- Fix logic to detect changes in oidc modules. [tottoto]
- Fix command to get current oidc config status. [tottoto]


4.5.6 (2020-09-11)
------------------
- Fix function to update identity group alias. [tottoto]
- Remove sys calls to modules that might not have access. [Terry Howe]
- Fix read file for py2. [Terry Howe]
- Read to file more copy arguments. [Terry Howe]
- Add base64 tests. [Terry Howe]
- Get better error message for read to file base64 encoding. [Terry
  Howe]
- Remove tests for deprecated auth_enable. [Terry Howe]
- Remove tests of deprecated policy_set. [Terry Howe]
- Do not use requests in oidc. [Terry Howe]


4.5.5 (2020-08-20)
------------------
- Add latest parameters to approle. [Terry Howe]
- Add cas support for write and configuration. [Terry Howe]
- Fix incorrect aws module names. [Terry Howe]
- Provide alternate oidc auth token. [Terry Howe]
- Use the authenticated Vault client's token instead of extracting it
  from params. [Lander Visterin]
- Revert makedocs change. [Terry Howe]
- Update argspec to use fallback instead of default. [ayav09]
- Downgrade sphinx-notfound-page due to weird sphinx error message.
  [André Frimberger]
- Introduce approle parameter "secret_id_bound_cidrs" and fix
  token_bound_cidrs. [André Frimberger]


4.5.4 (2020-07-17)
------------------
- Add default value of group_filter for idempotency on replay
  hashivault_auth_ldap [charlrvd]
- Add support for use_token_groups in auth_ldap, as its now supported by
  hvac. [Tiago Posse]


4.5.3 (2020-07-02)
------------------
- Remove deprecated from hashivault_policy module. [Terry Howe]
- Update hashivault_write docs. [Terry Howe]
- Fix doc build. [Terry Howe]
- Fix pki docs. [Terry Howe]
- Fix pki docs. [Terry Howe]
- Handle not existing approle role secret. [André Frimberger]


4.5.2 (2020-05-28)
------------------
- Remove redundant documentation from README. [Terry Howe]
- Add rules file to docs. [Terry Howe]
- Fix response 204 on pki_ca_set. Closes TerryHowe/ansible-modules-
  hashivault#256. [Tiago Posse]
- FIX: error with ansible-doc unknown doc-fragment hashivault. [ChiCuong
  HA]
- Add common_name doc string to CA. [Jamie Lennox]
- Add server_flag to pki_role. [Jamie Lennox]
- Add state documentation to policy. [Jamie Lennox]
- When doing state comparisons allow int/string mismatch. [Jamie Lennox]
- Fix hashivault_pki_ca docs. [Jamie Lennox]
- Use ASCII hypens in documentation. [Jamie Lennox]


4.5.1 (2020-05-12)
------------------
- Add issuer to k8s config. [Terry Howe]
- Initialize keys_updated. [Terry Howe]
- Do not use sys.auth to validate exists. [Terry Howe]
- Do not use sys/auth for change detection. [Terry Howe]
- Remove ansible docs that break sphinx. [Terry Howe]
- Fix docs for sphinx. [Terry Howe]


4.5.0 (2020-05-03)
------------------
- Rename read pki modules get. [Terry Howe]
- Rename pki set modules. [Terry Howe]
- Do not use deprecated module in test. [Terry Howe]
- Fix docs errors. [Terry Howe]
- Fix further pep8 issues. [Terry Howe]
- Pep8 for pki modules. [Terry Howe]
- Update the pki release version added. [Terry Howe]
- Fixed compare state function to work with Python 2. [Dr.MagPie]
- Adding pki tests. [Dr.MagPie]
- Adding pki modules. [Dr.MagPie]
- Adding centralized logic for pki modules. [Dr.MagPie]
- Deprecate some poorly named policy modules. [Terry Howe]
- Proper deprecating of modules. [Terry Howe]
- Remove register from hashivault_read. [Terry Howe]
- Add aws config module. [Terry Howe]
- Fix aws documentation. [Terry Howe]
- Fix up aws auth role. [Terry Howe]
- Add pycodestyle to travis. [Terry Howe]
- Use pycodestyle. [Terry Howe]
- Only pep8 the ansible directory. [Terry Howe]
- Fix pep8 problems. [Terry Howe]
- Fix some flake8 stuff. [Terry Howe]
- Clean up hashivault_init call. [Terry Howe]


4.4.7 (2020-04-28)
------------------
- Bring consul modules up to date. [Terry Howe]
- Add more verbosity to troubleshoot. [Damien Goldenberg]
- Remove deprecated module for secret engine. [Damien Goldenberg]
- Fix consul modules. [Damien Goldenberg]
- Add some tests for consul secret engine. [Damien Goldenberg]
- Upgrade hvac to have latest fix on the consul secret engine. [Damien
  Goldenberg]
- Add consul secret engine modules. [Damien Goldenberg]


4.4.6 (2020-04-27)
------------------
- Add pem_keys support to k8s. [Terry Howe]
- Get more consistent on mount_point handling. [Terry Howe]
- Centralized auth mount check. [Dr.MagPie]
- Centralized secret mount check. [Dr.MagPie]
- Centralising Common logic. [Dr.MagPie]
- Clean up default description. [Terry Howe]
- Set default value for description in secret_engine to handle
  idempotence. [André Frimberger]
- Remove no longer meaningful comment. [Terry Howe]
- Be consistent on list auth methods. [Terry Howe]
- Docs pep8 compliance. [Terry Howe]
- Fix for py27. [Terry Howe]
- Add aws header for auth. [Terry Howe]
- Make modules more robust. [Terry Howe]
- Remove old exception handling for now. [Terry Howe]


4.4.5 (2020-04-16)
------------------
- Login support for mount_point. [Terry Howe]
- Add missing fragment to module. [Terry Howe]
- Make sure upload script on master. [Terry Howe]
- Added editor config. [Dr.MagPie]
- Removed doc duplication. [Dr.MagPie]
- Check for uncommitted changes up upload script. [Terry Howe]
- Add pull to upload script. [Terry Howe]


4.4.4 (2020-04-16)
------------------
- Version 4.4.4. [Terry Howe]


4.4.3 (2020-04-16)
------------------
- Fix for ldap change. [Terry Howe]
- Fix document build. [Terry Howe]
- Removed default value for author. [Dr.MagPie]
- Updated makedocs.sh to use doc_fragments. [Dr.MagPie]
- Added doc_fragments hashivault.py to link.sh. [Dr.MagPie]
- Replaced duplicates with common doc. [Dr.MagPie]
- Added common doc. [Dr.MagPie]


4.4.2 (2020-04-15)
------------------
- Force audit path to end in / [Terry Howe]


4.4.1 (2020-04-14)
------------------
- Fix no_log issue for hashivault_write and others. [Terry Howe]
- Add missing tests. [Terry Howe]


4.4.0 (2020-04-14)
------------------
- Deprecate audit enable and add new module. [Terry Howe]


4.3.4 (2020-04-14)
------------------
- Doc fixes. [Terry Howe]
- Pep8 fixes. [Terry Howe]
- Add k8s tests. [Terry Howe]
- Kubernetes auth roles added. [Sergey Mikhaltsov]


4.3.3 (2020-04-13)
------------------
- Fix update for approle. [Terry Howe]


4.3.2 (2020-04-11)
------------------
- Support old full path format. [Terry Howe]
- Add scret engine test. [Terry Howe]
- Clean up secrets engine. [Terry Howe]
- Update viewitems lib to six. [Samy Coenen]
- Add support for python 2 with viewitems. [Samy Coenen]
- Remove default value version, update dictionary comparison. [Samy
  Coenen]


4.3.1 (2020-04-09)
------------------
- Clean up hashivault_auth_method. [Terry Howe]
- Avoid oid auth method config problem. [Terry Howe]


4.3.0 (2020-04-09)
------------------
- Fix for hvac 0.10.1. [Terry Howe]
- Added kubernetes auth module. [Sergey Mikhaltsov]
- Userpass: pass mount_point on create, too. [André Frimberger]
- Fix #207. [Philipp Hossner]
- Add test for changing token_bound_cidrs without pass. [André
  Frimberger]
- Add support for token_bound_cidrs in hashivault_userpass. [André
  Frimberger]
- Back out approad secret change and add tests. [Terry Howe]
- When a wrapped token is created, the response key is wrap_info Include
  cidr_list and wrap_ttl when custom_secret_id is not None. [Shawn
  Johnson]
- Fix identity delete group alias. [Terry Howe]
- Add hashivault_identity_group_alias module. [Michał Suszko]
- Add the module for managing group aliases + fix typo in entity_alias.
  [Guillaume Rémy]


4.2.4 (2020-03-20)
------------------
- Fix #204. [Philipp Hossner]
- Check HTTP status code with an array and fix 'exists' state.
  [Guillaume Rémy]
- Refactored the oidc_auth_role module. [Guillaume Rémy]
- Defaulting members to None when creating groups. [Guillaume Rémy]
- Pass mount_point, so current configuration for mointpoint other than
  "ldap" could be read. [Michał Suszko]


4.2.3 (2019-11-21)
------------------
- Provide logged alternate data for write to get returned data. [Terry
  Howe]
- Added new return var to auth mount. [DrMagPie]
- Added var to defirentiate new and updated engines. [DrMagPie]
- Enable OIDC auth and role in namespaces. [Lynn Dong]


4.2.2 (2019-10-29)
------------------
- Fix auth method. [Drew Mullen]


4.2.1 (2019-10-24)
------------------
- Add OIDC auth role and functional test. [Lynn Dong]
- Check mode param for auth method, clarify error. [Drew Mullen]
- Fix idemp for namespaces. [Drew Mullen]
- Updates to fix check mode regarding namespaces. [Drew Mullen]
- Pass check mode if no namespace. [Drew Mullen]


4.2.0 (2019-10-22)
------------------
- Deprecate hashivault_policy_set_from_file. [Terry Howe]
- Add OIDC auth method config module. [Lynn Dong]
- Altered hashivault_list.py to use the hvac list_secrets method. [Jason
  Neurohr]
- Fix db idempotency check. [Drew Mullen]
- Rename deprecated modules. [Terry Howe]
- Update examples to avoid deprecated modules. [Drew Mullen]
- Tune and disable should use secret_engine instead. [Drew Mullen]
- Deprecate tuning module. [Drew Mullen]
- Cast options[version] to string for idempotence check. [Drew Mullen]
- Fix some cases where casting raise exception. [Damien Goldenberg]


4.1.0 (2019-08-30)
------------------
- Version 4.1.0. [Terry Howe]
- Provide module to manage namespaces (ent only) [Drew Mullen]

  clean up comments
- Approle can accept params in a file with role_file. [Drew Mullen]


4.0.0 (2019-08-14)
------------------
- Deprecate create and delete approle modules. [Terry Howe]
- Add check_mode support for approle. [Terry Howe]
- Approle secret mount point support. [Terry Howe]
- Add proper approle modules. [Terry Howe]
- Added hashivault_ldap_group module. [Jason Neurohr]
- Make aws role create idempotent. [Terry Howe]
- Db engine config plugin can be used for all db plugins. [Damien
  Goldenberg]
- Added support for custom mount points. [DrMagPie]


3.18.2 (2019-08-06)
-------------------
- Fix the compatibility of the db role module with python 2.7. [Damien
  Goldenberg]


3.18.1 (2019-07-24)
-------------------
- Set no_log for some values. [Terry Howe]
- Fix some documentation typos. [Terry Howe]
- Fix the doc and upload script. [Terry Howe]


3.18.0 (2019-07-24)
-------------------
- Added hashivault_auth_ldap and hashivault_identity_group [Jason
  Neurohr]
- Updated hashivault_auth_list.py to return False for changed. [Jason
  Neurohr]
- Fix some pep warnings and docs issues. [Terry Howe]
- Fix various idempotence checks. [Drew Mullen]
- Secret eng mgmt. [Drew Mullen]


3.17.7 (2019-05-31)
-------------------
- Deprecate hashivault_auth_enable. [Terry Howe]
- Add new hashivault_auth_method module. [Drew Mullen]
- Add new hashivault_azure_auth_role module. [Drew Mullen]
- Add new hashivault_azure_auth_config module. [Drew Mullen]


3.17.6 (2019-05-23)
-------------------
- Azure configuration support. [Drew Mullen]
- Allow required_if, etc to be passed. [Drew Mullen]
- Make twine happy. [Terry Howe]


3.17.5 (2019-05-16)
-------------------
- Allow to create custom approle secret id. [Wojciech Podgorski]


3.17.4 (2019-04-25)
-------------------
- Fix kv2 secret write. [Vincent Mazenod]


3.17.3 (2019-04-11)
-------------------
- Add `mount_point` option to the lookup plugin. [Piotr Śliwka]


3.17.2 (2019-04-11)
-------------------
- Add the support for the http method and return json in case of GET
  method. [Damien Goldenberg]


3.17.1 (2019-04-05)
-------------------
- Support metadata for v1 reads. [Terry Howe]
- Convert to use twine. [Terry Howe]


3.17.0 (2019-04-05)
-------------------
- Add read metadata. [Terry Howe]
- Add functional tests. [Terry Howe]
- Add a module to fetch cluster health information. [Damien Goldenberg]
- Add a module to fetch leader information cluster. [Damien Goldenberg]
- Enable secret keystore. [Terry Howe]
- Add pep8 to tox.ini. [Terry Howe]
- Pep8 compliance. [Terry Howe]
- Start getting pep8 support. [Terry Howe]
- Clean up some warnings that are causing issues. [Terry Howe]


3.16.3 (2019-03-26)
-------------------
- Fix approle auth for hvac kv2 engine. [Nathan K]


3.16.2 (2019-03-02)
-------------------
- Add arguments to init. [Terry Howe]


3.16.1 (2019-02-27)
-------------------
- Add support for passing mount_point to hashivault_userpass. [Stanislav
  Yotov]


3.16.0 (2019-02-05)
-------------------
- Ansible galaxy support. [Maxime Brunet]


3.15.1 (2019-02-05)
-------------------
- Have write return data. [Terry Howe]
- Clean up imports. [Terry Howe]
- Get rid of inventory warnings. [Terry Howe]
- Add document metadata. [Terry Howe]


3.15.0 (2019-01-31)
-------------------
- Add tests for hashivault_userpass. [Terry Howe]
- Userpass user management module. [p0tr3c]


3.14.0 (2019-01-31)
-------------------
- Add tests for root token generation. [Terry Howe]
- Add support to generate root token & revoke tokens. [Bharath
  Channakeshava]


3.13.0 (2019-01-31)
-------------------
- kv2 secret read, write and delete with hvac kv2 client. [Terry Howe]
- Remove verbose call of playbook. [drewmullen]
- Initial kv2 support [rmullen]
- Identity entity tests. [Terry Howe]
- Fix entity update, will not overwrite with default on update. [p0tr3c]
- Fix unordered list comparison for policies. [p0tr3c]
- Add identity management module. [p0tr3c]
- Support for entity aliases. [p0tr3c]
- Make global env travis. [Terry Howe]


3.12.1 (2019-01-24)
-------------------
- Add pipeline job to build Ansible webdocs and publish to Github pages,
  Fix YAML. [Samy Coenen]


3.12.0 (2019-01-06)
-------------------
- Optionally include namespace as play parameter or environment var.
  [rmullen]


3.11.0 (2018-12-17)
-------------------
- Add tests for revoke and renew token. [Terry Howe]
- Added token renew and token revoke functions. [Charles Bevan]


3.10.1 (2018-11-14)
-------------------
- Fix auth_methods for LDAP and GitHub. [Eugene Kossyak]


3.10.0 (2018-11-12)
-------------------
- Stop using deprecated methods. [Terry Howe]
- Fix for hvac 0.7.0. [Terry Howe]
- Added method to get iam role from ec2 metadata. [simonmacklin]
- Added methods for iam auth. [Simon Macklin]
- Only set cacert and capath if env set. [Terry Howe]
- Fix missing cert info for lookups. [Clinton Judy]
- Fix hashivault_write secret parameter description. [Manuel Tiago
  Pereira]


3.9.8 (2018-10-11)
------------------
- Added AWS create role module. [Simon Macklin]
- Ad wrap_ttl support to approle secret create. [Terry Howe]
- Rename hashivault_policy_set_from_file and test. [Terry Howe]
- Update hashivault_policy_set_file.py. [drewmullen]
- Update README.rst. [drewmullen]
- New param, rules_file and set rules to open( rules_file content )
  [Drew Mullen]
- Add some unicode support. [Terry Howe]
- Add support of token from ansible environment. [Terry Howe]
- Override environment variables with ansible variables. [Terry Howe]
- Fix tests again. [Terry Howe]
- Get rid of extraneous spaces. [Terry Howe]
- Fix tests for list audit backends, list secret backends. [Terry Howe]
- Fix list policy tests and list auth backends test. [Terry Howe]
- Add period parameter on token creation. [Konstantin Privezentsev]


3.9.7 (2018-08-29)
------------------
- Secrets enable options support. [kevin2seedlink]
- Fix readme. [Clinton Judy]
- Comment out readonly token for now. [Terry Howe]
- Little better upload script. [Terry Howe]


3.9.6 (2018-07-04)
------------------
- Support VAULT_CACERT for lookup plugin. [Terry Howe]
- Improved documentation about export variables. [Ivan N]


3.9.5 (2018-05-19)
------------------
- Strip whitespace from vault token file contents. [George Pchelkin]
- Add parameters to approle create role secret. [Terry Howe]
- Add parameters to approle create role. [Terry Howe]


3.9.4 (2018-04-25)
------------------
- TLS auth option [Christopher Valles]


3.9.3 (2018-04-12)
------------------
- Make key optional for lookup plugin [Marcin Wolny]


3.9.2 (2018-03-18)
------------------
- Mark ttl and max_ttl changed if parsed values differ. [Terry Howe]


3.9.1 (2018-03-17)
------------------
- Add change log and gitchangelog. [Terry Howe]


3.9.0 (2018-03-03)
------------------
- Test refactor. [Terry Howe]
- Amend the hashivault_policy_get to return a failure status when a
  policy doesn't exist rather than a positive response with a Null set.
  [Danny Webb]
- Fix secret list and isolate test. [Terry Howe]


3.8.6 (2018-02-22)
------------------
- Revert the read in hashivault_write. [Terry Howe]
- Update docs of modules - authtype option. [Vladislav Saveliev]


3.8.5 (2018-02-20)
------------------
- Add installation instructions and bump release. [Terry Howe]
- Selectively enable check mode. [Marc Sensenich]
- Check for changes even if not updating. [Marc Sensenich]
- Revert changes to test.yml. [Marc Sensenich]
- Use local params to limit code changes. [Marc Sensenich]
- Add Check Mode to HashiVault Write. [Marc Sensenich]
- Automated tests for py3. [Terry Howe]


3.8.4 (2018-02-06)
------------------
- Py3 compatibility. [Terry Howe]


3.8.3 (2018-02-06)
------------------
- Rename file read/write to to/from. [Terry Howe]
- Created modules and action plugins for reading and writing file
  secrets. [GIBSON, NICHOLAS R]
- Change okifmissing to default. [Terry Howe]
- Added variable ok_if_missing to return an empty result if searched key
  does not exists. [Bruno Soares]


3.8.2 (2018-01-04)
------------------
- Check un/sealed and return correct status. [Carlo Blohm]
- Add example sandbox. [Terry Howe]


3.8.1 (2017-12-31)
------------------
- Add userpass tempate. [Terry Howe]
- Ldap and userpass support from env. [Terry Howe]


3.8.0 (2017-12-30)
------------------
- Add the rest of the approle modules. [Terry Howe]
- Minimum approle modules. [Terry Howe]
- Use templates for env files. [Terry Howe]
- Add namespace for approle and fix lookup plugin. [Terry Howe]
- Reuse test_secret rather than include. [Terry Howe]
- Add newline on env file. [Terry Howe]
- Added approle authentication. [GIBSON, NICHOLAS R]
- Allow update on non existing attribute. [Terry Howe]
- Split out secret and ephemeral testing. [Terry Howe]
- Read secrets only for update. [Terry Howe]
- Add changed flag support for hashivault_write. [Jean-Yves Rivallan]
- Add documentation for mount tune. [Terry Howe]


3.7.0 (2017-11-11)
------------------
- Fix up tune mount docs. [Terry Howe]
- Add mount tune module. [Marc Sensenich]


3.6.0 (2017-11-11)
------------------
- Use no_log on create user functional test. [Terry Howe]
- Fix hvac 0.3.0 change. [Terry Howe]
- Get rid of warnings for tests. [Terry Howe]
- See if travis deals with ipc locker better. [Terry Howe]


3.5.1 (2017-10-10)
------------------
- Add the ability to define a mount point for Auth backends. [Marc
  Sensenich]


3.5.0 (2017-10-04)
------------------
- Fix typos in module_utils/hashivault.py. [Nathan Randall]
- Add documentation for TLS auth support. [Nathan Randall]
- Add support for TLS connections via hvac client. [Nathan Randall]

  Adds support for using strong, (potentially) mutually-authenticated
  TLS connections to Hashicorp Vault API.

  Adds parameters to allow user to specify paths for client cert and
  client key in order to support TLS mutual authentication with Vault
  HTTP API, where the hvac client includes Python 'requests' and passes
  the client cert and client key as a tuple argument to the 'cert' param
  supplied to a requests.Session object. Depending on what params/values
  are supplied by user, the value for 'verify' (as passed to the
  requests.Session object) will be either True, False, or (preferrably)
  the path to a CA cert or directory of CA certs to use for TLS auth
  validation.

  Updates argument_spec with new params for TLS client authentication :

    - ca_cert
    - ca_path
    - client_cert
    - client_key

  Updates documentation with info about ^^new params^^ and their defaults.


3.4.1 (2017-07-31)
------------------
- Removed empty set fact in test. [Jaime Soriano Pastor]
- Don't try to remove a policy that doesn't exist. [Jaime Soriano
  Pastor]
- Don't enable auth backend if it's already enabled. [Jaime Soriano
  Pastor]
- Don't set policy if current policy is the same. [Jaime Soriano Pastor]
- Don't try to enable secret if it's already enabled. [Jaime Soriano
  Pastor]
- Add lookup token parameter. [Terry Howe]
- Add test audit back in. [Terry Howe]


3.4.0 (2017-07-28)
------------------
- Add better delete verification. [Terry Howe]
- Remove deprecated call from update. [Terry Howe]
- Add delete secret capability. [David de Sousa]


3.3.0 (2017-07-21)
------------------
- Added modules for rekey. [Bharath Channakeshava]
- Bumping version number. Setting no_parent type to bool, default False.
  [T.J. Telan]
- Bumping version number. Setting types for accessor and wrap_ttl. [T.J.
  Telan]
- Adding token create and token lookup modules. Adding an integration
  test with secrets and policies using non-root tokens. [T.J. Telan]
- Speeding up tests setting gather_facts to no. [T.J. Telan]
- Adding fixes for running tests in os x. [T.J. Telan]
- Merge remote-tracking branch 'upstream/master' [T.J. Telan]
- Adding example usage for hashivault_token_lookup. [T.J. Telan]
- Adding token lookup. [T.J. Telan]
- Supporting all of the options for the token create api call. [T.J.
  Telan]
- Adding support for creating tokens, and adding tests that do not use
  root_token. [T.J. Telan]
- Just refactoring. No more using fail. I negated the logic in their
  check and added it as an assert condition. [T.J. Telan]
- Starting some major work in test.yml to make it a bit more rigorous -
  We only need to provide VAULT_ADDR now. [T.J. Telan]
- Updating test_init.yml   * Adding names to tasks so it is easier to
  see which code paths were executed   * Reorganizing asserts under
  names   * Changed how we check on the keys, and root tokens using 'is
  defined' [T.J. Telan]
- Read task can read whole secrets. [Jaime Soriano Pastor]
- Add travis build badge. [Terry Howe]
- Fix test runner for travis. [Jaime Soriano Pastor]

  Mainly remove the dependency on mlock, that doesn't
  look allowed in travis sandbox.

  It also waits now for docker to be healthy instead of
  just for the open port.

  And some other refactorizations in start script to increase
  readability.
- Add build script. [Terry Howe]
- Add travis yml. [Terry Howe]
- Fix test for ansible 2.3.1.0. [Terry Howe]
- Write keys and tokens to file. [Terry Howe]
- Check to make sure VAULT_KEYS set for unseal test. [Terry Howe]


3.2.0 (2017-06-26)
------------------
- Add support for pgp public keys during vault init. [Bharath
  Channakeshava]


3.1.0 (2017-06-14)
------------------
- New release to set keys and threshold on init. [Terry Howe]
- Lots of things happened [Terry Howe]
- Create hashivault package. [Terry Howe]
