#!/bin/bash -ex
#
# Stop the test vault container
#
export NAME=${NAME:-test_vault}
docker stop $NAME 2>/dev/null || true
rm -f ./vaultenv.sh approlenv.sh
