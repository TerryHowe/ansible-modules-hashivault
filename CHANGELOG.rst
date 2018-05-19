Changelog
=========


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
