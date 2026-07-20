
# OPS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# source "$OPS_ROOT/lib/config.sh"

# source "$OPS_ROOT/lib/common.sh"

# source "$OPS_ROOT/lib/system.sh"


check_docker()
{
    echo "----------------"
    echo "Docker Subsystem"
    echo "----------------"

    # echo "Check Docker CLI"
    check_program "Docker CLI" docker

    echo
    echo "Checking Docker Compose..."
    if docker compose version >/dev/null 2>&1
    then
      local VERSION="$(docker compose version)"
      echo "${OK} Docker Compose is available"
      echo "  Version: ${VERSION}"
    fi

    # Check Docker Daemon
    echo
    echo "Checking Docker Daemon..."
    if docker ps >/dev/null 2>&1
    then
      echo "${OK} Docker Daemon is available"
    fi

}

check_container()
{
    # TODO:
    # Currently we query Docker once per container.
    # Future optimisation:
    # Pass each JSON object directly to check_container()
    # so docker compose ps is only executed once.

    local SERVICE_NAME="$1"
    local JSON
    local STATUS

    JSON="$(docker compose ps "$SERVICE_NAME" --format json)"
    STATUS=$?

    if [[ $STATUS -ne 0 ]]
    then
        echo "${ERROR} Service not found"
        return
    fi

    local SERVICE
    local STATE
    local HEALTH

    SERVICE="$(echo "$JSON" | jq -r '.Service')"
    STATE="$(echo "$JSON" | jq -r '.State')"
    HEALTH="$(echo "$JSON" | jq -r '.Health')"

    echo
    local TITLE="Container - $SERVICE"
    echo "$TITLE"
    printf '%*s\n' "${#TITLE}" '' | tr ' ' '-'

    # echo "${OK} Service : $SERVICE"
    echo "${OK} State   : $STATE"
    if [[ -z $HEALTH ]]
    then
        HEALTH="No health check"
    fi

    echo "${OK} Health  : $HEALTH"
    echo
}

check_all_containers()
{
    docker compose ps --format json |
    jq -r '.Service' |
    while read -r SERVICE
    do
        check_container "$SERVICE"
    done
}
