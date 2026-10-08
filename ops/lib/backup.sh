#!/usr/bin/env bash

create_backup_set() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d-%H-%M-%S')"

    BACKUP_SET_DIR="$BACKUP_STAGING_DIR/$timestamp"

    mkdir -p \
        "$BACKUP_SET_DIR/postgres" \
        "$BACKUP_SET_DIR/volumes" \
        "$BACKUP_SET_DIR/config"
}

backup_postgres() {
    set -o pipefail

    docker compose -f "$COMPOSE_FILE" exec -T postgres \
        pg_dump -U n8n -d n8n \
        | gzip > "$BACKUP_SET_DIR/postgres/n8n.sql.gz"

    docker compose -f "$COMPOSE_FILE" exec -T postgres \
        pg_dump -U n8n -d recipe_platform \
        | gzip > "$BACKUP_SET_DIR/postgres/recipe_platform.sql.gz"
}

backup_n8n_volume() {
    docker run --rm \
        -v n8n-lab_n8n_data:/data:ro \
        -v "$BACKUP_SET_DIR/volumes:/backup" \
        alpine \
        tar czf /backup/n8n_data.tar.gz -C /data .
}

backup_config() {
    cp "$COMPOSE_FILE" \
        "$BACKUP_SET_DIR/config/docker-compose-prod.yml"

    cp "$PROJECT_ROOT/cloudflared/config.yml" \
        "$BACKUP_SET_DIR/config/cloudflared-config.yml"
}

backup_ops() {
    tar czf "$BACKUP_SET_DIR/config/ops.tar.gz" \
        -C "$PROJECT_ROOT" ops
}

create_manifest() {
    cat > "$BACKUP_SET_DIR/backup-manifest.txt" <<EOF
Backup timestamp: $(date '+%Y-%m-%d %H:%M:%S')
Project: $PROJECT_NAME
Host: $(hostname)

Contents:
- postgres/n8n.sql.gz
- postgres/recipe_platform.sql.gz
- volumes/n8n_data.tar.gz
- config/docker-compose-prod.yml
- config/cloudflared-config.yml
- config/ops.tar.gz
EOF
}

create_checksums() {
    (
        cd "$BACKUP_SET_DIR"
        find postgres volumes config -type f -print0 \
            | sort -z \
            | xargs -0 sha256sum > checksums.sha256
    )
}

verify_checksums() {
    (
        cd "$BACKUP_SET_DIR"
        sha256sum -c checksums.sha256
    )
}

finalize_backup() {
    local backup_name

    backup_name="$(basename "$BACKUP_SET_DIR")"

    mkdir -p "$BACKUP_DAILY_DIR"

    mv "$BACKUP_SET_DIR" "$BACKUP_DAILY_DIR/$backup_name"
}

cleanup_old_backups() {
    find "$BACKUP_DAILY_DIR" \
        -mindepth 1 \
        -maxdepth 1 \
        -type d \
        -name '20??-??-??-??-??-??' \
        -mtime +"$BACKUP_RETENTION_DAYS" \
        -print
}

backup_google_drive() {
    local backup_name
    local local_backup
    local remote_backup

    backup_name="$(basename "$BACKUP_SET_DIR")"
    local_backup="$BACKUP_DAILY_DIR/$backup_name"
    remote_backup="$GOOGLE_DRIVE_REMOTE:n8n-lab-backups/$backup_name"

    rclone copy "$local_backup" "$remote_backup" \
        --stats-one-line \
        --stats 10s
}

verify_google_drive() {
    local backup_name
    local local_backup
    local remote_backup

    backup_name="$(basename "$BACKUP_SET_DIR")"
    local_backup="$BACKUP_DAILY_DIR/$backup_name"
    remote_backup="$GOOGLE_DRIVE_REMOTE:n8n-lab-backups/$backup_name"

    rclone check "$local_backup" "$remote_backup"
}

run_backup_stage() {
    local stage_function="$1"
    local success_message="$2"
    local failure_stage="$3"

    local stage_status
    local backup_name
    local staging_backup

    if "$stage_function"
    then
        success "$success_message"
        return "$EXIT_SUCCESS"
    else
        stage_status="$?"
        backup_name="$(basename "$BACKUP_SET_DIR")"
        staging_backup="$BACKUP_SET_DIR"

        error "$failure_stage failed"

        if send_backup_stage_failure_notification \
            "$backup_name" \
            "$failure_stage" \
            "$staging_backup" \
            "$failure_stage failed with exit status: $stage_status."
        then
            :
        else
            warn "Failed to send backup failure notification"
        fi

        return "$EXIT_ERROR"
    fi
}
