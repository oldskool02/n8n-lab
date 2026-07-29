
run_help() {
    cat <<EOF

Operations Toolkit

Usage:
    ops <command> [options]

Commands:

General:
    help    Show this message
    version Display the version information

Diagnostics
    doctor  Run the system diagnostics
    logs    Display logs for a service

Examples:
    ops version
    ops doctor
    ops logs n8n
    ops logs postgres --follow
    ops logs redis --tail 100
EOF
}