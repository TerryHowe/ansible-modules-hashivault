path "secret/bob/*" {
    capabilities = ["create", "read", "update", "delete", "list"]
}
path "secret/bob" {
    capabilities = ["list"]
}
