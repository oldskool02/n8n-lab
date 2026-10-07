#!/usr/bin/env bash

google_backup_path() {
    local backup_name="$1"

    printf '%s\n' \
        "$GOOGLE_DRIVE_REMOTE:n8n-lab-backups/$backup_name"
}

google_check_backup() {
    local backup_dir="$1"
    local backup_name
    local remote_path

    backup_name="$(basename "$backup_dir")"
    remote_path="$(google_backup_path "$backup_name")"

    print_message "Checking: $backup_name"

    if [[ ! -d "$backup_dir" ]]
    then
        error "Local backup directory does not exist: $backup_dir"
        return "$EXIT_ERROR"
    fi

    if [[ ! -f "$backup_dir/checksums.sha256" ]]
    then
        error "Backup checksums file is missing: $backup_dir/checksums.sha256"
        return "$EXIT_ERROR"
    fi

    if rclone check "$backup_dir" "$remote_path"
    then
        success "Google drive backup verified"
        return "$EXIT_SUCCESS"
    fi

    error "Google drive backup verification failed"
    return "$EXIT_ERROR"
}

google_reconcile_backup() {
    local backup_dir="$1"
    local backup_name
    local remote_path
    local answer

    backup_name="$(basename "$backup_dir")"
    remote_path="$(google_backup_path "$backup_name")"

    section "Google Drive Backup Reconciliation"

    print_message "Backup:  $backup_name"
    print_message "Local:   $backup_dir"
    print_message "Remote:  $remote_path"
    newline

    if [[ ! -d "$backup_dir" ]]
    then
        error "Local backup directory does not exist: $backup_dir"
        return "$EXIT_ERROR"
    fi

    if [[ ! -f "$backup_dir/checksums.sha256" ]]
    then
        error "Backup checksums file is missing: $backup_dir/checksums.sha256"
        return "$EXIT_ERROR"
    fi

    print_message "Checking local backup against Google Drive..."
    newline

    if rclone check "$backup_dir" "$remote_path"
    then
        success "Google Drive backup is already verified"
        return "$EXIT_SUCCESS"
    else
        local check_status="$?"

        if (( check_status != 1 ))
        then
            error "Unable to check the Google Drive backup"
            error "rclone check exited with status: $check_status"
            return "$EXIT_ERROR"
        fi
    fi

    warn "Google Drive backup requires reconciliation"
    newline

    print_message "The local backup will be used as the source"
    print_message "Only missing or different files will be uploaded"
    print_message "Existing matching files will not be re-uploaded"
    newline

    read -r -p "Proceed with reconciliation? [y/N] " answer

    if [[ ! "$answer" =~ ^[Yy]$ ]]
    then
        print_message "Reconciliation cancelled"
        return "$EXIT_SUCCESS"
    fi

    newline
    print_message "Reconciling Google Drive backup..."

    if ! rclone copy "$backup_dir" "$remote_path" \
        --stats-one-line \
        --stats 10s
    then
        error "Google Drive reconciliation failed"
        return "$EXIT_ERROR"
    fi

    success "Google Drive reconciliation upload completed"
    newline

    print_message "Verifying reconciled backup..."

    if rclone check "$backup_dir" "$remote_path"
    then
        success "Google Drive backup verified after reconciliation"
        return "$EXIT_SUCCESS"
    else
        local check_status=$?

        if (( check_status != 1 ))
        then
            error "Unable to check Google Drive backup"
            error "rclone check exited with status: $check_status"
            return "$EXIT_ERROR"
        fi
    fi

    error "Google Drive backup requires reconciliation"
    return "$EXIT_ERROR"
}

google_reconcile_all_backups() {
    local backup_dir
    local checked=0
    local verified=0
    local needs_reconciliation=0
    local failed=0
    local answer
    local -a pending_backups=()

    section "Google Drive Backup Reconciliation"

    while IFS= read -r backup_dir
    do
        checked=$((checked + 1 ))

        print_message "Checking: $(basename "$backup_dir")"

        if rclone check "$backup_dir" "$(google_backup_path "$(basename "$backup_dir")")"
        then
            verified=$((verified + 1))
            success "Already verified"
        else
            local check_status=$?

            if (( check_status != 1 ))
            then
                error "Unable to check: $(basename "$backup_dir")"
                failed=$((failed + 1))
            else
                needs_reconciliation=$((needs_reconciliation + 1))
                pending_backups+=("$backup_dir")
                warn "Requires reconciliation"
            fi
        fi

        newline

    done < <(
        find "$BACKUP_DAILY_DIR" \
            -mindepth 1 \
            -maxdepth 1 \
            -type d \
            -name '20??-??-??-??-??-??' \
            | sort
    )

    section "Summary"

    print_message "Backups checked:         $checked"
    print_message "Already verified:        $verified"
    print_message "Requires reconciliation: $needs_reconciliation"
    print_message "Check failures:          $failed"

    if (( failed > 0 ))
    then
        error "One or more backups could not be checked"
        return "$EXIT_ERROR"
    fi

    if (( needs_reconciliation == 0 ))
    then
        success "All backups are already verified"
        return "$EXIT_SUCCESS"
    fi

    print_message "Backups requiring reconciliation"
    for backup_dir in "${pending_backups[@]}"
    do
        print_message "    $(basename "$backup_dir")"
    done

    newline

    read -r -p "Proceed with reconciliation? [y/N] " answer

    if [[ ! "$answer" =~ ^[Yy]$ ]]
    then
        print_message "Reconciliation cancelled"
        return "$EXIT_SUCCESS"
    fi

    newline

    for backup_dir in "${pending_backups[@]}"
    do
        if google_reconcile_backup "$backup_dir"
        then
            :
        else
            failed=$((failed + 1))
        fi

        newline
    done

    if (( failed > 0 ))
    then
        error "One or more backups could not be reconciled"
        return "$EXIT_ERROR"
    fi

    success "All required Google Drive reconciliations completed"
    return "$EXIT_SUCCESS"
}

google_check_all_backups() {
    local backup_dir
    local checked=0
    local verified=0
    local failed=0

    section "Google Drive Backup Check"

    while IFS= read -r backup_dir
    do
        checked=$((checked + 1))

        if google_check_backup "$backup_dir"
        then
            verified=$((verified + 1))
        else
            failed=$((failed + 1))
        fi

        newline

    done < <(
        find "$BACKUP_DAILY_DIR" \
            -mindepth 1 \
            -maxdepth 1 \
            -type d \
            -name '20??-??-??-??-??-??' \
            | sort
    )

    section "Summary"
    print_message "Backups checked:        $checked"
    print_message "Backups verified:       $verified"
    print_message "Backups requiring work: $failed"

    if (( failed > 0 ))
    then
        return "$EXIT_ERROR"
    fi

    return "$EXIT_SUCCESS"
}
