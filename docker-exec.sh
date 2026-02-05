#!/usr/bin/env bash
set -euo pipefail

DOCKERFILE="${DOCKERFILE:-docker/Dockerfile_tests}"

find_repo_root() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -d "${dir}/.git" || -f "${dir}/.git" ]]; then
      echo "${dir}"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${ROOT}" ]]; then
  ROOT="$(find_repo_root || pwd)"
fi
BUILD_CONTEXT="${ROOT}"

if [[ "${DOCKERFILE}" != /* ]]; then
  DOCKERFILE="${ROOT}/${DOCKERFILE}"
fi

SUBDIR="${PWD#${ROOT}}"
WORKDIR="/work${SUBDIR}"

IMAGE="wb-fast-modbus-$(basename "${DOCKERFILE}" | tr '[:upper:]' '[:lower:]')"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <command> [args...]"
  echo "Env:"
  echo "  DOCKERFILE (default: ${DOCKERFILE})"
  exit 1
fi

if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
  echo "Docker image '${IMAGE}' not found. Building..."
  docker build -f "${DOCKERFILE}" -t "${IMAGE}" "${BUILD_CONTEXT}"
fi

CMD="$*"
CACHE_SETUP='export HOME=/work; export XDG_CACHE_HOME=/work/.cache; mkdir -p "$XDG_CACHE_HOME"'

TTY_ARGS=()
if [ -t 1 ]; then
  TTY_ARGS=(-it)
fi

docker run --rm "${TTY_ARGS[@]}" \
  --user "$(id -u):$(id -g)" \
  -v "${ROOT}":/work \
  -w "${WORKDIR}" \
  "${IMAGE}" \
  sh -lc "${CACHE_SETUP}; ${CMD}"
