#!/usr/bin/env bash
# Regenerate the src/shrub/_*.py dictionaries inside the shrub-dev container.
#
# The repo is bind-mounted at /shrub, so generated files land in your
# working tree -- review them with `git diff`.
#
# Order matters: generate_phi_dict.py cross-checks its tags against
# _dicom_dict.py, so the DICOM dictionary is generated first.
set -euo pipefail

IMAGE=localhost/shrub-dev
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! podman image exists "$IMAGE"; then
    echo "error: image '$IMAGE' not found. Build it first:" >&2
    echo "  podman build -t $IMAGE $REPO" >&2
    exit 1
fi

run() {
    podman run --rm -v "$REPO:/shrub" -w /shrub "$IMAGE" "$@"
}

run python utils/generate_dicom_dict.py
run python utils/generate_phi_dict.py
