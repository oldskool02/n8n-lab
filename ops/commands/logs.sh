#!/usr/bin/env bash

run_logs() {
    local service="${1:-}"
    local follow=false

    if [[ -z "$service" ]]
    then
        fatal "Service name required"
    fi

    if [[ "$2" == "--follow" ]]
    then
        follow=true
    fi

    show_service_logs "$service" "$follow"
}