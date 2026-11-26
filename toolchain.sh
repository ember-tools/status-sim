#!/usr/bin/env bash
#
# Build and verification commands for this repository.
#
# Every command runs from the repository root regardless of the caller's working directory, and
# inside the nix environment of shell.nix via `direnv exec`, so Python, pipenv and node are the
# pinned versions.
#
# Usage: ./toolchain.sh <command> [args...]
#        ./toolchain.sh <group> <command> [args...]
#        ./toolchain.sh help

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND="$ROOT/frontend"

# Runs a command inside the project's direnv/nix environment, or directly when direnv is missing.
run() {
    if [ -f "$ROOT/.envrc" ] && command -v direnv >/dev/null 2>&1; then
        if [ -z "${DIRENV_APPROVED:-}" ]; then
            if ! direnv exec "$ROOT" true >/dev/null 2>&1; then
                echo "toolchain: this checkout's .envrc has not been approved. Approve it once with:" >&2
                echo "               direnv allow $ROOT" >&2
                exit 1
            fi
            DIRENV_APPROVED=1
        fi
        direnv exec "$ROOT" "$@"
    else
        "$@"
    fi
}

usage() {
    cat <<'TEXT'
Usage: ./toolchain.sh <command> [args...]
       ./toolchain.sh <group> <command> [args...]

The first hyphen of a name also reads as a space, so `fe build` and `fe-build` are the same
command. `./toolchain.sh fe` lists what is in a group.

Frontend
  fe-install            npm install
  fe-install-clean      npm ci
  fe-dev                Vite dev server with the proxy to a local backend
  fe-typecheck          vue-tsc
  fe-bundle             Production build with the prerendered pages
  fe-lint [name] [args] Every linter of @emberbox/lint, as frontend/emberbox-lint.config.mjs sets
                        them up, failing when one does.
                        With a name only that one: eslint, duplication, browser-storage,
                        em-dash, comments
  fe-audit              All linters, non-gating; prints everything they find
  fe-eslint [args]      ESLint directly
  fe-build              Full verification: linters, type check and build

Backend
  be-install            pipenv sync --dev
  be-dev                uvicorn with reload on port 8000
  be-test               pytest
  be-test1 <expr>       pytest -k <expr>
  be-scenarios          Validate every scenario file in src/static/scenarios
  be-verify             Tests and scenario validation

Docker
  docker-build          Build the production image
  docker-app            Start the local stack (compose.yml with Redis), always rebuilt
  docker-app-down       Stop the local stack

Whole repository
  verify                Everything CI runs
  help                  This text
TEXT
}

fe() { cd "$FRONTEND"; }
be() { cd "$ROOT"; }

COMMAND_GROUPS=(fe be docker)

is_group() {
    local candidate
    for candidate in "${COMMAND_GROUPS[@]}"; do
        [ "$1" = "$candidate" ] && return 0
    done
    return 1
}

# Lists a group's commands, read from the case arms below so the listing cannot drift.
list_group() {
    sed -n 's/^    \([a-z][a-z0-9|_-]*\)).*/\1/p' "$ROOT/toolchain.sh" |
        tr '|' '\n' | sed -n "s/^$1-//p"
}

if is_group "${1:-}"; then
    if [ $# -ge 2 ]; then
        set -- "$1-$2" "${@:3}"
    else
        echo "Commands in '$1':" >&2
        list_group "$1" | sed "s|^|  $1 |" >&2
        exit 2
    fi
fi

cmd="${1:-help}"
shift || true

case "$cmd" in
    fe-install)       fe; run npm install "$@" ;;
    fe-install-clean) fe; run npm ci "$@" ;;
    fe-dev)           fe; run npm run dev -- "$@" ;;
    fe-typecheck)     fe; run npx vue-tsc -b "$@" ;;
    fe-bundle)        fe; run npx vite build "$@" ;;
    fe-lint)          fe; run npx emberbox-lint "$@" ;;
    fe-audit)         fe; run npx emberbox-lint --audit ;;
    fe-eslint)        fe; run npx eslint "$@" ;;
    fe-build)
        "$ROOT/toolchain.sh" fe-lint
        "$ROOT/toolchain.sh" fe-typecheck
        "$ROOT/toolchain.sh" fe-bundle
        ;;

    be-install)       be; run pipenv sync --dev "$@" ;;
    be-dev)           be; run pipenv run uvicorn main:app --app-dir src --reload --port 8000 "$@" ;;
    be-test)          be; run pipenv run pytest "$@" ;;
    be-test1)
        [ $# -ge 1 ] || { echo "be-test1 needs a pytest -k expression" >&2; exit 2; }
        be; run pipenv run pytest -k "$@"
        ;;
    be-scenarios)     be; run pipenv run python tests/test_scenario_validation.py ;;
    be-verify)
        "$ROOT/toolchain.sh" be-test
        "$ROOT/toolchain.sh" be-scenarios
        ;;

    docker-build)     be; run docker build . "$@" ;;
    docker-app)       be; run docker compose up -d --build "$@" ;;
    docker-app-down)  be; run docker compose down "$@" ;;

    verify)
        "$ROOT/toolchain.sh" be-verify
        "$ROOT/toolchain.sh" fe-build
        ;;

    help|-h|--help) usage ;;
    *) echo "Unknown command: $cmd" >&2; echo >&2; usage >&2; exit 2 ;;
esac
