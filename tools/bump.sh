#!/usr/bin/env bash
set -euo pipefail

# Simple tag bumper: increments the numeric suffix after 'dev-'
# Usage: tools/bump.sh

ENV_FILE=".env"

# Create .env if missing
if [ ! -f "$ENV_FILE" ]; then
  echo "FRONTEND_TAG=dev-1" > "$ENV_FILE"
  echo "BACKEND_TAG=dev-1" >> "$ENV_FILE"
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

bump_tag() {
  local tag="$1"
  local prefix suffix
  prefix="${tag%%-*}"
  suffix="${tag##*-}"
  if [[ "$tag" != *-* ]] || ! [[ "$suffix" =~ ^[0-9]+$ ]]; then
    echo "${tag}-1"
  else
    local next=$((suffix + 1))
    echo "${prefix}-${next}"
  fi
}

NEW_FRONTEND_TAG=$(bump_tag "${FRONTEND_TAG:-dev-1}")
NEW_BACKEND_TAG=$(bump_tag "${BACKEND_TAG:-dev-1}")

# Write back
{
  echo "FRONTEND_TAG=${NEW_FRONTEND_TAG}"
  echo "BACKEND_TAG=${NEW_BACKEND_TAG}"
} > "$ENV_FILE"

echo "Bumped tags -> FRONTEND_TAG=$NEW_FRONTEND_TAG, BACKEND_TAG=$NEW_BACKEND_TAG"

echo "Next: docker-compose up --build -d"

