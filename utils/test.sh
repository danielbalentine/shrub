#!/usr/bin/env bash
# Run pytest inside the shrub-dev container, with the repo bind-mounted
# at /shrub.
#
# Arguments are passed straight to pytest; with none, runs all of tests/.
#   ./utils/test.sh
#   ./utils/test.sh tests/test_data_invariants.py
#   ./utils/test.sh tests/test_action_codes.py::TestActionCodes::<name> -v
set -euo pipefail

IMAGE=localhost/shrub-dev
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! podman image exists "$IMAGE"; then
    echo "error: image '$IMAGE' not found. Build it first:" >&2
    echo "  ./utils/build.sh" >&2
    exit 1
fi

if [ "$#" -eq 0 ]; then
    set -- tests/
fi

podman run --rm -v "$REPO:/shrub" -w /shrub "$IMAGE" python -m pytest "$@"
