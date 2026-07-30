#!/usr/bin/env bash

run_logs() {
    local service="${1:-}"
    local follow=false
    local tail=50

    if [[ -z "$service" || "$service" == -* ]]
    then
        error "Service Name required"
        run_logs_help
        return "$EXIT_ERROR"
    fi

    shift

    while [[ $# -gt 0 ]]
    do
        case "$1" in
            --follow)
                follow=true
                shift
            ;;
            --tail)
                if [[ -z "$2" || "$2" == -* ]]
                then
                    error "Option '--tail' requires a numeric value"
                    run_logs_help
                    return "$EXIT_ERROR"
                fi
                tail="$2"
                shift
                shift
                ;;
            *)
                error "Unknown option '$1'"
                run_logs_help
                return "$EXIT_ERROR"

        esac
    done

    show_service_logs "$service" "$follow" "$tail"
}
