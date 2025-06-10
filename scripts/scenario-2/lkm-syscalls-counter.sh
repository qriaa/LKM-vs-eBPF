#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

PERF_RESULTS_PATH=$SCRIPT_DIR/../../results/scenario-2/perf-data/lkm-syscalls-counter.data
MODULE_FILE=$SCRIPT_DIR/../../lkm/syscalls-counter/syscalls-counter.ko
MODULE_NAME='syscalls_counter'
FUNCTIONS=(
    '__x64_sys_execve'
    '__x64_sys_openat'
    '__x64_sys_read'
    '__x64_sys_write'
)

insmod $MODULE_FILE

for FUNCTION_NAME in "${FUNCTIONS[@]}"; do
    sudo perf probe --add "$FUNCTION_NAME"
    sudo perf probe --add "$FUNCTION_NAME%return"
done;

# -m increases buffer amount, prevents losing chunks
# -e "cycles/call-graph=dwarf/" \
perf record -a -m 16M -o $PERF_RESULTS_PATH \
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

rmmod $MODULE_NAME
