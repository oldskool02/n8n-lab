
# OPS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# source "$OPS_ROOT/lib/config.sh"

readonly OK="✔️"
readonly ERROR="❌"
readonly WARNING="⚠️"
readonly INFO="ℹ️"

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
        echo "${ERROR} ${DISPLAY_NAME} is NOT installed"
    fi

    echo
}
