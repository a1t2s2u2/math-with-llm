#!/bin/bash
set -e

CODE_FILE="/tmp/check_${RANDOM}.lean"
echo "$LEAN_CODE" > "$CODE_FILE"

timeout 10s lean "$CODE_FILE" 2>&1 || exit_code=$?

if [ $exit_code -eq 124 ]; then
    echo "TIMEOUT"
    exit 1
fi

exit 0
