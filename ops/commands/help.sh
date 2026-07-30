#!/usr/bin/env bash

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

run_logs_help() {
    cat <<EOF

Operations Toolkit (logs)

Usage:
    ops logs <service> [options]

Options:
    --follow            Follow log output
    --tail <lines>      Show the last <lines> log entries
    --timestamps        Show timestamps
EOF
}