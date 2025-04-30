#!/bin/sh
source ./scripts/inc.sh

# write_session "run-action-done" "${1}"
log "end_debug: screenshot file  $(take_screenshot "${1}")"