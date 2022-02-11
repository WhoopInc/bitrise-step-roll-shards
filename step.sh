#!/bin/bash
set -euxo pipefail

CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${CURR_DIR}"

pip3 install requests

ROLLED_BUILD_SLUGS=$( python3 ./roll.py )
envman add --key "ROLLED_BUILD_SLUGS" --value "ROLLED_BUILD_SLUGS"
echo "ROLLED_BUILD_SLUGS: ${ROLLED_BUILD_SLUGS}"