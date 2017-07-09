#!/bin/bash -ex
#
# Stop the test vault container
#
NAME=${NAME:-test_vault}
docker stop $NAME 2>/dev/null || true
rm -f ./vaultenv.sh
