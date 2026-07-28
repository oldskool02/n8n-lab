
check_docker() {
    echo "----------------"
    echo "Docker Subsystem"
    echo "----------------"

    # echo "Check Docker CLI"
    check_program "Docker CLI" docker

    echo
    echo "Checking Docker Compose..."
    if version="$(docker compose version 2>/dev/null 2>&1)"
    then
      success "Docker Compose is available"
      detail "Version" "${version}"
    else
      error "Docker Compose is not available"
      exit "$EXIT_ERROR"
    fi

    # Check Docker Daemon
    echo
    echo "Checking Docker Daemon..."
    if docker ps >/dev/null 2>&1
    then
      success "Docker Daemon is available"
    #   echo "${OK} Docker Daemon is available"
    else
      error "Docker Daemon is not available"
      exit "$EXIT_ERROR"
    fi

}

# check_container() {
#     # TODO:
#     # Currently we query Docker once per container.
#     # Future optimisation:
#     # Pass each JSON object directly to check_container()
#     # so docker compose ps is only executed once.

#     local SERVICE_NAME="$1"
#     local JSON
#     local STATUS

#     JSON="$(docker compose ps "$SERVICE_NAME" --format json)"
#     STATUS=$?

#     if [[ $STATUS -ne 0 ]]
#     then
#         echo "${ERROR} Service not found"
#         return
#     fi

#     local SERVICE
#     local STATE
#     local HEALTH

#     SERVICE="$(echo "$JSON" | jq -r '.Service')"
#     STATE="$(echo "$JSON" | jq -r '.State')"
#     HEALTH="$(echo "$JSON" | jq -r '.Health')"

#     echo
#     local TITLE="Container - $SERVICE"
#     echo "$TITLE"
#     printf '%*s\n' "${#TITLE}" '' | tr ' ' '-'

#     # echo "${OK} Service : $SERVICE"
#     echo "${OK} State   : $STATE"
#     if [[ -z $HEALTH ]]
#     then
#         HEALTH="No health check"
#     fi

#     echo "${OK} Health  : $HEALTH"
#     echo
# }

check_container() {
    # TODO:
    # Currently we query Docker once per container.
    # Future optimisation:
    # Pass each JSON object directly to check_container()
    # so docker compose ps is only executed once.

    local CONTAINER="$1"
    local SERVICE
    local STATE
    local HEALTH
    local IMAGE

    SERVICE="$(jq -r '.Service' <<< "$CONTAINER")"
    STATE="$(jq -r '.State' <<< "$CONTAINER")"
    HEALTH="$(jq -r '.Health // "No health check"' <<< "$CONTAINER")"
    IMAGE="$(jq -r '.Image' <<< "$CONTAINER")"

    newline
    local TITLE="Service - $SERVICE"
    echo "$TITLE"
    printf '%*s\n' "${#TITLE}" '' | tr ' ' '-'

    # echo "${OK} Service : $SERVICE"
    echo "${OK} State   : $STATE"
    echo "${OK} Health  : $HEALTH"
    echo "      Image   : $IMAGE"
    echo
}

check_all_containers() {
    docker compose ps --format json |
    jq -c '.' |
    while read -r CONTAINER
    do
        check_container "$CONTAINER"
    done
    # get_service_statuses |
    # while read -r SERVICE_STATUS
    # do
    #   SERVICE="$(jq -r '.Service' <<< "$SERVICE_STATUS")"
    #   STATE="$(jq -r '.State' <<< "$SERVICE_STATUS")"
    #   HEALTH="$(jq -r '.Health' <<< "$SERVICE_STATUS")"
    #   IMAGE="$(jq -r '.Image' <<< "$SERVICE_STATUS")"
    # done

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
