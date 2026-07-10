#!/usr/bin/env bash

set -Eeuo pipefail

OPS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

source "$OPS_ROOT/lib/config.sh"

echo "===================================="
echo " Operations Toolkit"
echo "===================================="
echo

echo "Project : $PROJECT_NAME"
echo "Author  : $PROJECT_AUTHOR"
echo "Version : $(cat "$VERSION_FILE")"
