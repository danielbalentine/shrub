#!/usr/bin/env bash
# Build the localhost/shrub-dev image from the repo's Containerfile.
#
# The image holds only Python and the pinned dev dependencies
# (requirements-dev.txt). The code itself is bind-mounted at run time,
# so rebuild only when requirements-dev.txt or the Containerfile change.
set -euo pipefail

IMAGE=localhost/shrub-dev
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

podman build -t "$IMAGE" "$REPO"
