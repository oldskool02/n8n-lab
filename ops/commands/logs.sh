run_logs() {
    local service="${1:-}"

    if [[ -z "$service" ]]
    then
        fatal "Service name required"
    fi

    show_service_logs "$service"
}