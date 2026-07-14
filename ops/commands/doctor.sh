#!/usr/bin/env bash

set -Eeuo pipefail

OPS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

source "$OPS_ROOT/lib/config.sh"

source "$OPS_ROOT/lib/common.sh"


check_program()
{
    # Assumption
    # The executable supports "--version"
    # If we encounter exceptions in future, refactor this function


    local DISPLAY_NAME="$1"
    local COMMAND_NAME="$2"
    # VERSION="$("$COMMAND_NAME" --version)"

    echo "Checking ${DISPLAY_NAME}..."

    if command -v "$COMMAND_NAME" >/dev/null 2>&1
    then
        local VERSION="$("$COMMAND_NAME" --version)"
        echo "${OK} ${DISPLAY_NAME} is installed"
        echo "  Version : ${VERSION}"
    else
        echo "${FAIL} ${DISPLAY_NAME} is NOT installed"
    fi

    echo
}

check_docker()
{
    echo "----------------"
    echo "Docker Subsystem"
    echo "----------------"

    # echo "Check Docker CLI"
    check_program "Docker CLI" docker

    echo
    echo "Check Docker Compose"
    if docker compose version >/dev/null 2>&1
    then
      local VERSION="$(docker compose version)"
      echo "${OK} Docker Compose is available"
      echo "  Version: ${VERSION}"
    fi

    echo
    echo "Check Docker Daemon"
    if docker ps >/dev/null 2>&1
    then
      local VERSION="$(docker ps)"
      echo "${OK} Docker Daemon is available"
    #   echo "  Version: ${VERSION}"
    fi

    # Check Docker Daemon
}

echo "=================================="
echo " Operations Toolkit - Doctor"
echo "=================================="
echo

# check_program "Docker" docker
check_program "Git" git
check_program "Python" python3

check_docker
