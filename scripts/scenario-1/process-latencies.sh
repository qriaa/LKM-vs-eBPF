#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

PERF_RESULTS_PATH="$SCRIPT_DIR/../../results/scenario-1/perf-data/"
LATENCIES_PATH="$SCRIPT_DIR/../../results/scenario-1/latency-data/"
TESTS=(
    'control-firewall'
    'lkm-firewall'
    'ebpf-nf-firewall'
    'ebpf-xdp-firewall'
)
FUNCTION='net_rx_action'


mkdir -p $LATENCIES_PATH

. $SCRIPT_DIR/../../.venv/bin/activate

for TEST in "${TESTS[@]}"; do
    echo "Processing latencies for $TEST..."
    python3 scripts/latency.py \
        -i "${PERF_RESULTS_PATH}${TEST}.data" \
        -o "${LATENCIES_PATH}${TEST}.json" \
        -p "${FUNCTION}"
done
