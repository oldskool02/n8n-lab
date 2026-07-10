#!/usr/bin/env bash

set -Eeuo pipefail

OPS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

source "$OPS_ROOT/lib/config.sh"

OK="✔️"
FAIL="❌"

check_program()
{
    # Assumption
    # The executable supports "--version"
    # If we encounter exceptions in future, refactor this function


    local DISPLAY_NAME="$1"
    local COMMAND_NAME="$2"
    VERSION="$("$COMMAND_NAME" --version)"

    echo "Checking ${DISPLAY_NAME}..."

    if command -v "$COMMAND_NAME" >/dev/null 2>&1
    then
        echo "${OK} ${DISPLAY_NAME} is installed"
        echo "   Version : ${VERSION}"
    else
        echo "${FAIL} ${DISPLAY_NAME} is NOT installed"
    fi

    echo
}


echo "=================================="
echo " Operations Toolkit - Doctor"
echo "=================================="
echo

check_program "Docker" docker
check_program "Git" git
check_program "Python" python3
