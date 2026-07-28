
check_program()
{
    # Assumption
    # The executable supports "--version"
    # If we encounter exceptions in future, refactor this function


    local DISPLAY_NAME="$1"
    local COMMAND_NAME="$2"
    # VERSION="$("$COMMAND_NAME" --version)"

    checking "${DISPLAY_NAME}"

    if command -v "$COMMAND_NAME" >/dev/null 2>&1
    then
        local VERSION
        VERSION="$("$COMMAND_NAME" --version)"
        success "${DISPLAY_NAME} is installed"
        detail "  Version" "${VERSION}"
    else
        error "${DISPLAY_NAME} is NOT installed"
        return "$EXIT_ERROR"
    fi

    newline
}
