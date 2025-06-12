#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

PERF_RESULTS_PATH=$SCRIPT_DIR/../../results/scenario-2/perf-data/control-syscalls-counter.data
FUNCTIONS=(
    '__x64_sys_execve'
    '__x64_sys_openat'
    '__x64_sys_read'
    '__x64_sys_write'
)

for FUNCTION_NAME in "${FUNCTIONS[@]}"; do
    sudo perf probe --add "$FUNCTION_NAME"
    sudo perf probe --add "$FUNCTION_NAME%return"
done;

# -m increases buffer amount, prevents losing chunks
perf record -a -m 32M -o $PERF_RESULTS_PATH \
    -e "cycles/call-graph=dwarf/" \
    -e "cpu-clock/call-graph=dwarf/" \
    -e "probe:__x64_sys_execve/call-graph=no/" \
    -e "probe:__x64_sys_execve__return/call-graph=no/" \
    -e "probe:__x64_sys_openat/call-graph=no/" \
    -e "probe:__x64_sys_openat__return/call-graph=no/" \
    -e "probe:__x64_sys_read/call-graph=no/" \
    -e "probe:__x64_sys_read__return/call-graph=no/" \
    -e "probe:__x64_sys_write/call-graph=no/" \
    -e "probe:__x64_sys_write__return/call-graph=no/" &
PERF_PID=$!

sleep 2
# run workload
for ((i = 0 ; i < 10000 ; i++ )); do
    ls
done

kill -s SIGINT $PERF_PID
wait $PERF_PID

for FUNCTION_NAME in "${FUNCTIONS[@]}"; do
    sudo perf probe --del "$FUNCTION_NAME"
    sudo perf probe --del "${FUNCTION_NAME}__return"
done;
