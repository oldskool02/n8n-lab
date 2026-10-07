#!/usr/bin/env bash

run_google() {
    local action="${1:-all}"

    case "$action" in
        all)
            google_reconcile_all_backups
            ;;

        check)
            google_check_all_backups
            ;;

        20??-??-??-??-??-??)
            google_reconcile_backup "$BACKUP_DAILY_DIR/$action"
            ;;

        *)
            error "Unknown google action: $action"
            newline
            print_message "Usage:"
            print_message "    ops google check"
            print_message "    ops google <backup-id>"
            return "$EXIT_ERROR"
            ;;
    esac
}
