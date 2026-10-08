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

Diagnostics:
    doctor  Run the system diagnostics
    logs    Display logs for a service
    health  Check production service health
    recover Check and recover unhealthy services

Backup:
    backup  Create and verify a production backup
            - PostgreSQL - n8n + recipe_platform
            - n8n data volume
            - Production configuration
            - Ops tooling
            - Manifest
            - Checksums
            - Local verification
            - Finalize into backups/daily/
            - Upload to Google Drive
            - Verify the Google Drive copy

External Backup (Google)
    google              - Reconcile all local backups
    google check        - Check all backups
    google <backup_id>  - Reconcile one backup

Examples:
    ops version
    ops doctor
    ops health
    ops recover
    ops logs n8n
    ops logs postgres --follow
    ops logs redis --tail 100
    ops backup
    ops google
    ops google check
    ops google <backup_id>
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