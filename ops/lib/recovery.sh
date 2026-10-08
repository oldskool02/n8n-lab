#!/usr/bin/env bash

wait_for_service() {
    local service="$1"
    local attempts="$RECOVERY_ATTEMPTS"
    local attempt=1

    while (( attempt <= attempts ))
    do
        case "$service" in
            postgres)
                if check_postgres
                then
                    return "$EXIT_SUCCESS"
                fi
                ;;
            redis)
                if check_redis
                then
                    return "$EXIT_SUCCESS"
                fi
                ;;
            n8n)
                if check_n8n
                then
                    return "$EXIT_SUCCESS"
                fi
                ;;
            n8n-worker)
                if check_n8n_worker
                then
                    return "$EXIT_SUCCESS"
                fi
                ;;
            recipe-platform)
                if check_recipe_platform
                then
                    return "$EXIT_SUCCESS"
                fi
                ;;
            recipe-frontend)
                if check_recipe_frontend
                then
                    return "$EXIT_SUCCESS"
                fi
                ;;
            cloudflared)
                if check_cloudflared
                then
                    return "$EXIT_SUCCESS"
                fi
                ;;
            *)
                error "Unknown service: $service"
                return "$EXIT_ERROR"
                ;;
        esac

        if (( attempt < attempts ))
        then
            sleep "$RECOVERY_WAIT_SECONDS"
        fi

        (( attempt++ ))
    done

    return "$EXIT_ERROR"
}


recover_service() {
    local service="$1"

    info "Restarting $service"

    if ! docker compose -f "$COMPOSE_FILE" restart "$service"
    then
        error "$service restart failed"
        return "$EXIT_ERROR"
    fi

    success "$service restart completed"
    info "Waiting for $service to become healthy"

    if wait_for_service "$service"
    then
        success "$service recovered successfully"
        return "$EXIT_SUCCESS"
    else
        error "$service did not recover"
        return "$EXIT_ERROR"
    fi
}