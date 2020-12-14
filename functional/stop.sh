#!/bin/bash -ex
#
# Stop the test vault container
#
export NAME=${NAME:-test_vault}
export AGENTNAME=${NAME:-testvaultagent}
docker stop $NAME 2>/dev/null || true
docker stop $AGENTNAME 2>/dev/null || true
rm -f ./vaultenv.sh approlenv.sh
