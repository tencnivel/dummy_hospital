#!/bin/sh
set -eu

echo "Synchronizing application dependencies..."
uv sync --frozen --extra dev

if [ "$#" -eq 0 ]; then
    echo "No command was provided to the container." >&2
    exit 1
fi

# Execute the command specified by the app service's `command` in docker-compose.yaml.
exec "$@"
