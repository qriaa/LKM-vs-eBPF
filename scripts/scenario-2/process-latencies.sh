#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

PERF_RESULTS_PATH=$SCRIPT_DIR/../../results/scenario-2/perf-data/
LATENCIES_PATH=$SCRIPT_DIR/../../results/scenario-2/latency-data/
TESTS=(
    'control-syscalls-counter'
    'lkm-syscalls-counter'
    'ebpf-syscalls-counter'
)
FUNCTIONS=(
    '__x64_sys_execve'
    '__x64_sys_openat'
    '__x64_sys_read'
    '__x64_sys_write'
)

mkdir -p $LATENCIES_PATH


for TEST in "${TESTS[@]}"; do
    echo "Processing latencies for $TEST..."
    python3 scripts/latency.py \
        -i "${PERF_RESULTS_PATH}${TEST}.data" \
        -o "${LATENCIES_PATH}${TEST}.json" \
        -p "${FUNCTIONS[@]}"
done
