#!/usr/bin/env bash


send_ops_email() {
    local recipient="$1"
    local subject="$2"
    local body="$3"

    printf 'To: %s\nSubject: %s\n\n%s\n' \
        "$recipient" \
        "$subject" \
        "$body" \
        | msmtp "$recipient"
}

send_backup_failure_notification() {
    local backup_id="$1"
    local failure_stage="$2"
    local local_backup="$3"
    local error_info="$4"

    local subject
    local body

    subject="[OPS ALERT] Production backup failed - $backup_id"

    body="Production backup failure detected

Backup ID:
$backup_id

Failure stage:
$failure_stage

Local backup:
$local_backup

Status:
The local backup has been retained.

Error:
$error_info

Recovery:
Run:
ops google $backup_id"

    send_ops_email "$OPS_ALERT_EMAIL" "$subject" "$body"

}

send_backup_stage_failure_notification() {
    local backup_id="$1"
    local failure_stage="$2"
    local staging_backup="$3"
    local error_info="$4"

    local subject
    local body

    subject="[OPS ALERT] Production backup failed - $backup_id"

    body="Production backup failure detected.

Backup ID:
$backup_id

Failure Stage:
$failure_stage

Backup Staging:
$staging_backup

Status:
The backup was not finalized.

Error:
$error_info

Recovery:
Review the staging backup and rerun:
ops backup"

    send_ops_email "$OPS_ALERT_EMAIL" "$subject" "$body"
}
