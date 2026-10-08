#!/usr/bin/env bash

run_recover() {
    section "Service Recovery"

    local failed=0

    if ! check_postgres
    then
        recover_service "postgres" || failed=1
    fi

    if ! check_redis
    then
        recover_service "redis" || failed=1
    fi

    if ! check_n8n
    then
        recover_service "n8n" || failed=1
    fi

    if ! check_n8n_worker
    then
        recover_service "n8n-worker" || failed=1
    fi

    if ! check_recipe_frontend
    then
        recover_service "recipe-frontend" || failed=1
    fi

    if ! check_recipe_platform
    then
        recover_service "recipe-platform" || failed=1
    fi

    if ! check_cloudflared
    then
        recover_service "cloudflared" || failed=1
    fi

    if (( failed == 0 ))
    then
        success "All services are healthy. No recovery required"
        return "$EXIT_SUCCESS"
    fi

    error "One or more services require recovery"
    return "$EXIT_ERROR"
}
