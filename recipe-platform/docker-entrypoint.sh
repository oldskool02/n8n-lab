#!/bin/sh

set -e
: "${INACTIVITY_TIMEOUT_MINUTES:?INACTIVITY_TIMEOUT_MINUTES is required}"
: "${INACTIVITY_WARNING_MINUTES:?INACTIVITY_WARNING_MINUTES is required}"

sed \
    -e "s|\${INACTIVITY_TIMEOUT_MINUTES}|${INACTIVITY_TIMEOUT_MINUTES}|g" \
    -e "s|\${INACTIVITY_WARNING_MINUTES}|${INACTIVITY_WARNING_MINUTES}|g" \
    /usr/share/nginx/html/config.js.template \
    > /usr/share/nginx/html/config.js

exec /docker-entrypoint.sh "$@"
