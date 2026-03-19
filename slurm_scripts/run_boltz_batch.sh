#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# Args
# -----------------------------
PROTEIN="$1"
BOLTZ_DIR="$2"
THREADS="$3"
LOG_FILE="$4"
shift 4

YAMLS=("$@")

# -----------------------------
# Logging setup
# -----------------------------
mkdir -p "$(dirname "$LOG_FILE")"

# Redirect all output to log + console
exec > >(tee -a "$LOG_FILE") 2>&1

echo "======================================="
echo "[run_boltz_batch] Starting"
echo "Protein: $PROTEIN"
echo "Threads: $THREADS"
echo "Num YAMLs: ${#YAMLS[@]}"
echo "Timestamp: $(date)"
echo "======================================="

# -----------------------------
# Main loop
# -----------------------------
for yaml in "${YAMLS[@]}"; do

    name=$(basename "$yaml" .yaml)
    OUT_DIR="${BOLTZ_DIR}/${name}"

    echo "[run_boltz_batch] Processing: $name"

    if [ -f "$OUT_DIR/complete.flag" ]; then
        echo "[run_boltz_batch] Skipping $name (already finished)"
        continue
    fi

    mkdir -p "$OUT_DIR"

    echo "[run_boltz_batch] Running Boltz..."
    bash ../slurm_scripts/run_boltz.sh "$yaml" "$OUT_DIR" "$THREADS"

    touch "$OUT_DIR/complete.flag"
    echo "[run_boltz_batch] Completed: $name"

done

echo "[run_boltz_batch] Batch complete"
echo "Timestamp: $(date)"
echo "======================================="