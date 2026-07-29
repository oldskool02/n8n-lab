#!/usr/bin/env bash

check_docker() {
    section "Docker Subsystem"

    check_program "Docker CLI" docker

    newline
    checking "Docker Compose"
    if version="$(docker compose version 2>/dev/null 2>&1)"
    then
      success "Docker Compose is available"
      detail "Version" "${version}"
    else
      error "Docker Compose is not available"
      exit "$EXIT_ERROR"
    fi

    # Check Docker Daemon
    newline
    checking "Docker Daemon"
    if docker ps >/dev/null 2>&1
    then
      success "Docker Daemon is available"
    else
      error "Docker Daemon is not available"
      exit "$EXIT_ERROR"
    fi

}

show_service_status() {

    local service_status="$1"
    local service
    local state
    local health
    local image
    local title

    service="$(jq -r '.Service' <<< "$service_status")"
    state="$(jq -r '.State' <<< "$service_status")"
    health="$(jq -r '.Health | if . == null or . == "" then "No health check" else . end' <<< "$service_status")"
    image="$(jq -r '.Image' <<< "$service_status")"

    title="Service - $service"

    newline
    print_message "$title"
    underline "$title"

    print_message "${OK} State   : $state"
    print_message "${OK} Health  : $health"
    print_message "   Image   : $image"
    newline
}

check_all_services() {
    get_service_statuses |
    while read -r service_status
    do
        show_service_status "$service_status"
    done
    newline
}

get_service_statuses() {
    docker compose ps --format json |
    jq -c '
        {
            Service: .Service,
            State: .State,
            Health: (.Health // "No health check"),
            Image: .Image
        }
    '
}

show_service_logs() {
  local service
  service="$1"

  docker compose logs "$service"
}
