############################################################
# Messaging Framework
############################################################

############################################################
# Layout
############################################################
detail() {
    local label="$1"
    local value="$2"

    printf ' %-10s: %s\n' "$label" "$value"

}

checking() {
    local name="$1"

    printf 'Checking %s......\n' "$name"
}

newline() {
    printf "\n"
}


############################################################
# Status Messages
############################################################
success() {
    local message="$1"
    local formatted_message

    formatted_message="$(format_message "success" "$message")"

    print_message "$formatted_message"
}


info() {
    local message="$1"
    local formatted_message

    formatted_message="$(format_message "info" "$message")"

    print_message "$formatted_message"
}

warn() {
    local message="$1"
    local formatted_message

    formatted_message="$(format_message "warning" "$message")"

    print_message "$formatted_message"
}

error() {
    local message="$1"
    local formatted_message

    formatted_message="$(format_message "error" "$message")"

    print_message "$formatted_message"

}

fatal() {
    local message="$1"

    error "$message"

    exit "$EXIT_FATAL"
}


print_message() {
    local message="$1"

    printf '%s\n' "$message"
}

format_message() {
    local level="$1"
    local message="$2"
    local prefix

    case "$level" in
        success)
            prefix="${OK} Success"
            ;;
        warning)
            prefix="${WARNING} Warning"
            ;;
        info)
            prefix="${INFO} Info"
            ;;
        error)
            prefix="${FAIL} ERROR"
            ;;
        *)
            prefix="$level"
            ;;
    esac

    printf '%s: %s' "$prefix" "$message"
}
