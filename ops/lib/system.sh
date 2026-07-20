
# OPS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# source "$OPS_ROOT/lib/config.sh"

# source "$OPS_ROOT/lib/common.sh"

check_system()
{
    # check_program "Docker" docker
    check_program "Git" git
    check_program "Python" python3
    check_program "jq" jq

}