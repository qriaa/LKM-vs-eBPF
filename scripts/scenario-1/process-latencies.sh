#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

PROBED_FUNCTION='net_rx_action'
TESTS=(
    'lkm-firewall'
    'ebpf-nf-firewall'
    'ebpf-xdp-firewall'
)

PERF_DATA_DIR="$SCRIPT_DIR/../../results/scenario-1/perf-data/"
LATENCY_CHARTS_DIR="$SCRIPT_DIR/../../results/scenario-1/latency-charts/"

mkdir -p $LATENCY_CHARTS_DIR

. $SCRIPT_DIR/../../.venv/bin/activate

for TEST in "${TESTS[@]}"; do
    python3 $SCRIPT_DIR/../latency.py \
        -f "${PERF_DATA_DIR}${TEST}.data" \
        -p "$PROBED_FUNCTION" \
        -c "${LATENCY_CHARTS_DIR}${TEST}.png"
done
