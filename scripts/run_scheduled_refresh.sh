#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"

DAYS="${DAYS:-90}"
MAX_FILES="${MAX_FILES:-4}"
ORDER="${ORDER:-latest}"

RUN_TS="$(date -u +"%Y%m%dT%H%M%SZ")"
LOG_FILE="${LOG_DIR}/pipeline_refresh_${RUN_TS}.log"

CONDA_SH="${HOME}/miniconda3/etc/profile.d/conda.sh"

mkdir -p "${LOG_DIR}"

{
  echo "RCI GDELT SEA scheduled refresh"
  echo "================================"
  echo "UTC run timestamp: ${RUN_TS}"
  echo "Project root: ${PROJECT_ROOT}"
  echo "Days: ${DAYS}"
  echo "Max files: ${MAX_FILES}"
  echo "Order: ${ORDER}"
  echo "Extra args: $*"
  echo ""

  if [ ! -f "${CONDA_SH}" ]; then
    echo "ERROR: Conda activation script not found at ${CONDA_SH}"
    exit 1
  fi

  # Load conda shell support, then activate the project environment.
  source "${CONDA_SH}"
  conda activate elt

  cd "${PROJECT_ROOT}"

  echo "Using Python:"
  which python
  python --version
  echo ""

  echo "Starting pipeline..."
  python scripts/run_pipeline.py \
    --days "${DAYS}" \
    --max-files "${MAX_FILES}" \
    --order "${ORDER}" \
    "$@"

  echo ""
  echo "Scheduled refresh completed successfully."
} 2>&1 | tee "${LOG_FILE}"

echo ""
echo "Log saved to: ${LOG_FILE}"