#!/usr/bin/env bash

run_backup() {
    section "Production Backup"

    create_backup_set

    print_message "Backup staging directory:"
    print_message "    $BACKUP_SET_DIR"
    newline

    print_message "Backing up PostgreSQL..."
    if ! run_backup_stage \
        backup_postgres \
        "PostgreSQL backup complete" \
        "PostgreSQL backup"
    then
        return "$EXIT_ERROR"
    fi

    print_message "Backing up n8n data..."
    if ! run_backup_stage \
        backup_n8n_volume \
        "n8n data backup complete" \
        "n8n data backup"
    then
        return "$EXIT_ERROR"
    fi

    print_message "Backing up production configuration..."

    if ! run_backup_stage \
        backup_config \
        "Production configuration backup complete" \
        "Production configuration"
    then
        return "$EXIT_ERROR"
    fi

    print_message "Backing up operations tooling..."
    if ! run_backup_stage \
        backup_ops \
        "Operations tooling backup complete" \
        "Operations tooling"
    then
        return "$EXIT_ERROR"
    fi

    print_message "Creating backup manifest..."
    if ! run_backup_stage \
        create_manifest \
        "Backup manifest created" \
        "Backup manifest"
    then
        return "$EXIT_ERROR"
    fi

    print_message "Creating checksums..."
    if ! run_backup_stage \
        create_checksums \
        "Checksums created" \
        "Checksums"
    then
        return "$EXIT_ERROR"
    fi

    print_message "Verifying backup..."
    if ! run_backup_stage \
        verify_checksums \
        "Backup verification passed" \
        "Backup verification"
    then
        return "$EXIT_ERROR"
    fi

    if finalize_backup
    then
        success "Local backup completed"
    else
        local finalize_status="$?"
        local backup_name
        local staging_backup

        backup_name="$(basename "$BACKUP_SET_DIR")"
        staging_backup="$BACKUP_SET_DIR"

        error "Backup finalisation failed"

        if send_backup_stage_failure_notification \
            "$backup_name" \
            "Backup finalization" \
            "$staging_backup" \
            "Backup finalization failed with exit status: $finalize_status"
        then
            :
        else
            warn "Failed to send backup failure notification"
        fi

        return "$EXIT_ERROR"
    fi

    print_message "Uploading backup to Google Drive..."
    if backup_google_drive
    then
        success "Google Drive upload complete"
    else
        local backup_status="$?"
        local backup_name
        local local_backup

        backup_name="$(basename "$BACKUP_SET_DIR")"
        local_backup="$BACKUP_DAILY_DIR/$backup_name"

        error "Google Drive upload failed"

        if send_backup_failure_notification \
            "$backup_name" \
            "Google Drive upload" \
            "$local_backup" \
            "Google Drive upload failed with exit status $backup_status"
        then
            :
        else
            warn "Failed to send backup failure notification"
        fi
        return "$EXIT_ERROR"
    fi

    print_message "Verifying Google Drive backup..."

    if verify_google_drive
    then
        success "Google Drive verification passed"
    else
        local verification_status="$?"
        local backup_name
        local local_backup

        backup_name="$(basename "$BACKUP_SET_DIR")"
        local_backup="$BACKUP_DAILY_DIR/$backup_name"

        error "Google Drive verification failed"

        if send_backup_failure_notification \
            "$backup_name" \
            "Google Drive verification" \
            "$local_backup" \
            "Google Drive verification failed with exit status: $verification_status."
        then
            :
        else
            warn "Failed to send backup failure notification"
        fi

        return "$EXIT_ERROR"
    fi

    print_message "Backup location:"
    print_message "    $BACKUP_DAILY_DIR/$(basename "$BACKUP_SET_DIR")"

    return "$EXIT_SUCCESS"
}
