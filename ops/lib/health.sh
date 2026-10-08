#!/usr/bin/env bash

check_n8n() {
    if curl -fsS --max-time 5 http://127.0.0.1:5678/healthz >/dev/null
    then
        success "n8n is healthy"
        return 0
    else
        error "n8n is unhealthy"
        return 1
    fi
}

check_n8n_worker() {
    local worker_process
    local task_runner_process

    worker_process="$(docker compose -f "$COMPOSE_FILE" exec -T n8n-worker ps aux 2>/dev/null | grep -E '[n]ode /usr/local/bin/n8n worker')"
    task_runner_process="$(docker compose -f "$COMPOSE_FILE" exec -T n8n-worker ps aux 2>/dev/null | grep -E '[@]n8n/task-runner.*dist/start.js')"

    if [[ -n "$worker_process" && -n "$task_runner_process" ]]
    then
        success "n8n-worker is healthy"
        return 0
    else
        error "n8n-worker is unhealthy"
        return 1
    fi
}

check_recipe_platform() {
    if docker compose -f "$COMPOSE_FILE" exec -T recipe-frontend \
        wget -qO- --timeout=5 http://recipe-platform:8000/docs >/dev/null
    then
        success "Recipe Platform is healthy"
        return 0
    else
        error "Recipe Platform is unhealthy"
        return 1
    fi
}


check_recipe_frontend() {
    if docker compose -f "$COMPOSE_FILE" exec -T recipe-frontend \
        wget -qO- --timeout=5 http://127.0.0.1/ >/dev/null
    then
        success "Recipe Frontend is healthy"
        return 0
    else
        error "Recipe Frontend is unhealthy"
        return 1
    fi
}

check_cloudflared() {
    local container_status

    container_status="$(docker inspect --format '{{.State.Status}}' n8n-lab-cloudflared-1 2>/dev/null)"

    if [[ "$container_status" != "running" ]]
    then
        error "Cloudflared container is not running"
        return 1
    fi

    if ! curl -fsS --max-time 10 https://oldskooln8n.xyz/healthz >/dev/null
    then
        error "Cloudflared n8n route is unhealthy"
        return 1
    fi

    if ! curl -fsS --max-time 10 https://recipes.oldskooln8n.xyz/ >/dev/null
    then
        error "Cloudflared Recipe route is unhealthy"
        return 1
    fi

    success "Cloudflared is healthy"
    return 0
}

check_postgres() {
    local health

    health="$(docker compose -f "$COMPOSE_FILE" ps --format json postgres | jq -r '.Health')"

    if [[ "$health" == "healthy" ]]
    then
        success "PostgreSQL is healthy"
        return 0
    else
        error "PostgreSQL is unhealthy: $health"
        return 1
    fi
}

check_redis() {
    if [[ "$(docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping 2>/dev/null)" == "PONG" ]]
    then
        success "Redis is healthy"
        return 0
    else
        error "Redis is unhealthy"
        return 1
    fi
}

check_health () {
    section "Service Health"

    local failed=0

    check_postgres || failed=1
    check_redis || failed=1
    check_n8n || failed=1
    check_n8n_worker || failed=1
    check_recipe_platform || failed=1
    check_recipe_frontend || failed=1
    check_cloudflared || failed=1

    return "$failed"
}